import json
import os
import re
import time
import random
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ==========================
# CONFIG
# ==========================
CANVAS_BASE_URL = "https://YOUR_SCHOOL.instructure.com"

# Persistent Chrome profile folder (stores your logged-in session cookies)
PROFILE_DIR = os.path.abspath("./chrome_profile_canvas")

OUT_FILE = "canvas_snapshot.json"

# First run: keep False so you can complete SSO/MFA and then press Enter.
# After you confirm it works, set True to skip the pause.
SKIP_LOGIN_PAUSE = False

# Extra safety caps
MAX_COURSES = None          # e.g. 5 to limit per run, or None for all
MAX_ASSIGNMENTS_PER_COURSE = None  # e.g. 30, or None for all

DETAIL_PAGE_TIMEOUT_SEC = 60


# ==========================
# Helpers
# ==========================
def now_iso():
    return datetime.now(timezone.utc).isoformat()


def human_sleep(min_sec: float, max_sec: float):
    """Sleep for a random duration to mimic human browsing."""
    duration = random.uniform(min_sec, max_sec)
    time.sleep(duration)


def long_break():
    """Occasional long pause to avoid constant pacing."""
    duration = random.uniform(15, 30)
    print(f"😴 Taking a longer break ({duration:.1f}s)")
    time.sleep(duration)


def start_driver():
    opts = Options()
    opts.add_argument(f"--user-data-dir={PROFILE_DIR}")
    opts.add_argument("--start-maximized")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    return driver


def ensure_logged_in(driver):
    driver.get(urljoin(CANVAS_BASE_URL, "/"))
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

    if not SKIP_LOGIN_PAUSE:
        print("\n🔐 Log into Canvas normally in the opened Chrome window (SSO/MFA).")
        print("✅ When you see a logged-in Canvas page, come back here.")
        input("Press Enter to continue once you are logged in...")


def get_soup(driver, timeout=60) -> BeautifulSoup:
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
    return BeautifulSoup(driver.page_source, "html.parser")


def normalize_space(s: str) -> str:
    return " ".join(s.split()).strip()


def try_get_text(el):
    if not el:
        return None
    t = el.get_text(" ", strip=True)
    t = normalize_space(t)
    return t if t else None


def parse_course_links_from_courses_page(soup: BeautifulSoup):
    courses = []
    for a in soup.select('a[href^="/courses/"]'):
        href = a.get("href", "")
        m = re.match(r"^/courses/(\d+)$", href)
        if not m:
            continue
        course_id = int(m.group(1))
        name = a.get_text(strip=True)
        if not name:
            continue
        courses.append({"id": course_id, "name": name, "url": urljoin(CANVAS_BASE_URL, href)})

    # Dedup by id
    dedup = {c["id"]: c for c in courses}
    return list(dedup.values())


def get_courses(driver):
    driver.get(urljoin(CANVAS_BASE_URL, "/courses"))
    soup = get_soup(driver, timeout=60)
    return parse_course_links_from_courses_page(soup)


def get_assignments_list_for_course(driver, course_id: int):
    """
    Scrape /courses/<id>/assignments to collect assignment IDs + URLs + titles.
    """
    driver.get(urljoin(CANVAS_BASE_URL, f"/courses/{course_id}/assignments"))
    soup = get_soup(driver, timeout=60)

    assignments = []
    for a in soup.select(f'a[href^="/courses/{course_id}/assignments/"]'):
        href = a.get("href", "")
        m = re.match(rf"^/courses/{course_id}/assignments/(\d+)", href)
        if not m:
            continue

        assignment_id = int(m.group(1))
        title = a.get_text(strip=True)
        if not title:
            continue

        assignments.append({
            "id": assignment_id,
            "title": title,
            "url": urljoin(CANVAS_BASE_URL, href),
        })

    # Dedup by assignment id
    dedup = {x["id"]: x for x in assignments}
    return list(dedup.values())


def extract_assignment_detail(soup: BeautifulSoup):
    """
    Best-effort extraction from an assignment detail page.
    Canvas HTML varies by theme/settings, so we:
      - store raw text versions
      - store raw HTML for instructions
      - try multiple heuristics for deadlines/points/submission types
    """

    # --- Instructions / description ---
    desc_el = soup.select_one(".user_content")
    instructions_text = try_get_text(desc_el)
    instructions_html = str(desc_el) if desc_el else None

    # --- Due info ---
    due_at_iso = None
    due_at_text = None

    # Try <time datetime="..."> elements with nearby "due"
    time_candidates = soup.select("time[datetime]")
    for t in time_candidates:
        text = normalize_space(t.get_text(" ", strip=True))
        dt_attr = t.get("datetime")
        nearby = normalize_space((t.parent.get_text(" ", strip=True) if t.parent else text).lower())
        if "due" in nearby or "due" in text.lower():
            due_at_iso = dt_attr
            due_at_text = text
            break

    # Fallback: look for any block that mentions due
    if due_at_text is None:
        meta_blocks = soup.select(".assignment_dates, .assignment-details, .details, .assignment__dates")
        for block in meta_blocks:
            block_text = normalize_space(block.get_text(" ", strip=True))
            if "due" in block_text.lower():
                due_at_text = block_text
                break

    # --- Availability text (best-effort snippets) ---
    page_text = normalize_space(soup.get_text(" ", strip=True))
    available_from_text = None
    until_text = None

    if "available" in page_text.lower():
        idx = page_text.lower().find("available")
        available_from_text = page_text[max(0, idx - 60): idx + 160]

    if "until" in page_text.lower():
        idx = page_text.lower().find("until")
        until_text = page_text[max(0, idx - 60): idx + 160]

    # --- Points possible (best effort) ---
    points_possible = None
    pts_candidates = soup.find_all(string=re.compile(r"\bpts\b|\bPoints?\b", re.IGNORECASE))
    for s in pts_candidates[:40]:
        t = normalize_space(str(s))
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:pts|points?)\b", t, re.IGNORECASE)
        if m:
            try:
                points_possible = float(m.group(1))
                if points_possible.is_integer():
                    points_possible = int(points_possible)
            except Exception:
                points_possible = None
            if points_possible is not None:
                break

    # --- Submission types (best effort) ---
    submission_types = []
    label_candidates = soup.find_all(
        string=re.compile(r"Submission Type|File Upload|Text Entry|Website URL|External Tool|Online", re.IGNORECASE)
    )
    for s in label_candidates[:80]:
        t = normalize_space(str(s)).lower()
        if "file upload" in t:
            submission_types.append("online_upload")
        if "text entry" in t:
            submission_types.append("online_text_entry")
        if "website url" in t:
            submission_types.append("online_url")
        if "external tool" in t:
            submission_types.append("external_tool")
    submission_types = sorted(set(submission_types))

    # --- Attachments (best effort) ---
    attachments = []
    for a in soup.select('a[href]'):
        text = a.get_text(strip=True)
        href = a.get("href", "")
        if not text or not href:
            continue
        if re.search(r"\.(pdf|docx?|pptx?|xlsx?|zip|png|jpe?g|txt)$", text, re.IGNORECASE):
            attachments.append({"filename": text, "url": urljoin(CANVAS_BASE_URL, href)})

    # --- External tool URL (best effort) ---
    external_tool_url = None
    for a in soup.select('a[href*="external_tools"], a[href*="lti"], a[href*="launch"]'):
        href = a.get("href")
        if href:
            external_tool_url = urljoin(CANVAS_BASE_URL, href)
            break

    return {
        "due_at_iso": due_at_iso,
        "due_at_text": due_at_text,
        "available_from_text": available_from_text,
        "until_text": until_text,
        "points_possible": points_possible,
        "instructions_text": instructions_text,
        "instructions_html": instructions_html,
        "submission_types": submission_types,
        "external_tool_url": external_tool_url,
        "attachments": attachments,
    }


def enrich_assignment_with_detail(driver, assignment):
    driver.get(assignment["url"])
    soup = get_soup(driver, timeout=DETAIL_PAGE_TIMEOUT_SEC)
    assignment["detail"] = extract_assignment_detail(soup)
    return assignment


def main():
    driver = start_driver()
    try:
        ensure_logged_in(driver)

        courses = get_courses(driver)
        if not courses:
            print("\n⚠️ No courses found on /courses. You may not be logged in yet.")
            print("Set SKIP_LOGIN_PAUSE=False and try again.")
            return

        # Randomize order to avoid predictable traversal patterns
        random.shuffle(courses)

        if MAX_COURSES is not None:
            courses = courses[:MAX_COURSES]

        snapshot = {
            "synced_at": now_iso(),
            "canvas_base_url": CANVAS_BASE_URL,
            "courses": [],
        }

        for course_idx, c in enumerate(courses, start=1):
            print(f"\n📘 ({course_idx}/{len(courses)}) Opening course: {c['name']}")
            human_sleep(8, 15)  # pause before entering a new course

            assignments = get_assignments_list_for_course(driver, c["id"])

            # Optional: cap per course
            if MAX_ASSIGNMENTS_PER_COURSE is not None:
                assignments = assignments[:MAX_ASSIGNMENTS_PER_COURSE]

            # Randomize assignment order
            random.shuffle(assignments)

            enriched = []
            for idx, a in enumerate(assignments, start=1):
                # Gentle pacing between assignment detail pages
                human_sleep(2.0, 5.0)

                try:
                    enriched.append(enrich_assignment_with_detail(driver, a))
                except Exception as e:
                    a["detail_error"] = str(e)
                    enriched.append(a)

                # Every ~10 assignments, take a longer break
                if idx % 10 == 0:
                    long_break()

            snapshot["courses"].append({
                "id": c["id"],
                "name": c["name"],
                "url": c["url"],
                "assignments": enriched,
            })

            print(f"✅ Finished course: {c['name']} ({len(enriched)} assignments)")
            human_sleep(10, 20)  # long pause between courses

        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Saved to {OUT_FILE}")
        print("Tip: after one good run, set SKIP_LOGIN_PAUSE=True to skip the login pause.")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
