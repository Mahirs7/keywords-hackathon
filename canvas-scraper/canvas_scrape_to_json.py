import json
import os
import re
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service



# ==========================
# CONFIG
# ==========================
CANVAS_BASE_URL = "https://canvas.illinois.edu/"

# Persistent Chrome profile folder (stores your logged-in session cookies)
PROFILE_DIR = os.path.abspath("./chrome_profile_canvas")

OUT_FILE = "canvas_snapshot.json"

# Set True after you’ve logged in once and confirmed it works
SKIP_LOGIN_PAUSE = False


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def start_driver():
    opts = Options()
    opts.add_argument(f"--user-data-dir={PROFILE_DIR}")
    opts.add_argument("--start-maximized")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    return driver


def ensure_logged_in(driver):
    """
    Opens Canvas. If this is your first run, complete SSO/MFA manually.
    After that, Canvas should keep you logged in via the saved Chrome profile.
    """
    driver.get(urljoin(CANVAS_BASE_URL, "/"))

    # Wait for page to load
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

    if not SKIP_LOGIN_PAUSE:
        print("\n🔐 If Canvas/SSO login appears, log in normally in the opened Chrome window.")
        print("✅ When you see your Canvas dashboard (or any logged-in Canvas page), come back here.")
        input("Press Enter to continue once you are logged in...")


def get_courses(driver):
    """
    Scrape courses from /courses page (usually reliable across Canvas themes).
    """
    courses_url = urljoin(CANVAS_BASE_URL, "/courses")
    driver.get(courses_url)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

    soup = BeautifulSoup(driver.page_source, "html.parser")

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

    # Dedup
    dedup = {c["id"]: c for c in courses}
    return list(dedup.values())


def parse_due_text(raw: str):
    """
    Keep due date as raw text initially; later we can normalize to ISO once we see your formatting.
    """
    t = " ".join(raw.split()).strip()
    return t if t else None


def get_assignments_for_course(driver, course_id: int):
    """
    Scrape /courses/<id>/assignments list.
    """
    url = urljoin(CANVAS_BASE_URL, f"/courses/{course_id}/assignments")
    driver.get(url)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

    soup = BeautifulSoup(driver.page_source, "html.parser")
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

        container = a.find_parent(["li", "tr", "div"])
        due_text = None
        if container:
            near_text = container.get_text(" ", strip=True)
            # heuristic: pull any phrase containing "Due"
            if "due" in near_text.lower():
                due_text = parse_due_text(near_text)

        assignments.append({
            "id": assignment_id,
            "title": title,
            "url": urljoin(CANVAS_BASE_URL, href),
            "due_text_raw": due_text,
        })

    dedup = {x["id"]: x for x in assignments}
    return list(dedup.values())


def main():
    driver = start_driver()
    try:
        ensure_logged_in(driver)

        # Quick sanity: if you're not logged in, /courses may redirect back to login.
        courses = get_courses(driver)
        if not courses:
            print("\n⚠️ I didn't find any courses on /courses.")
            print("This usually means you're not actually logged in yet, or your Canvas uses a different courses page layout.")
            print("Try setting SKIP_LOGIN_PAUSE=False and log in again, then rerun.")
            return

        snapshot = {
            "synced_at": now_iso(),
            "canvas_base_url": CANVAS_BASE_URL,
            "courses": [],
        }

        for c in courses:
            time.sleep(0.5)  # be gentle
            assignments = get_assignments_for_course(driver, c["id"])
            snapshot["courses"].append({
                "id": c["id"],
                "name": c["name"],
                "url": c["url"],
                "assignments": assignments,
            })
            print(f"Course {c['id']} — {c['name']}: {len(assignments)} assignments")

        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Saved to {OUT_FILE}")
        print("Tip: after you confirm it works once, set SKIP_LOGIN_PAUSE=True so it won’t prompt you again.")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
