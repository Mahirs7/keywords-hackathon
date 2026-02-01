"""
Canvas scraper - fetches assignments for a single course URL.
Used by the backend to sync assignments from user's course_sources (Canvas links).
"""

import re
import time
from typing import Optional, List, Dict
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    ChromeDriverManager = None

CANVAS_BASE_URL = "https://canvas.illinois.edu/"


def _parse_course_id_from_url(course_url: str) -> Optional[int]:
    """Extract Canvas numeric course id from URL like https://canvas.illinois.edu/courses/66465"""
    path = urlparse(course_url).path
    m = re.match(r"^/courses/(\d+)(?:/.*)?$", path)
    return int(m.group(1)) if m else None


def _parse_due_text(raw: str) -> Optional[str]:
    t = " ".join(raw.split()).strip()
    return t if t else None


def get_assignments_for_course(driver: webdriver.Chrome, course_id: int) -> List[Dict]:
    """
    Scrape /courses/<id>/assignments for one course.
    Returns list of {id, title, url, due_text_raw}.
    """
    url = urljoin(CANVAS_BASE_URL, f"/courses/{course_id}/assignments")
    driver.get(url)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
    time.sleep(0.5)

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
            if "due" in near_text.lower():
                due_text = _parse_due_text(near_text)
        assignments.append({
            "id": assignment_id,
            "title": title,
            "url": urljoin(CANVAS_BASE_URL, href),
            "due_text_raw": due_text,
        })

    dedup = {x["id"]: x for x in assignments}
    return list(dedup.values())


def scrape_assignments_for_course_url(
    course_url: str,
    *,
    headless: bool = True,
    driver: Optional[webdriver.Chrome] = None,
    profile_dir: Optional[str] = None,
) -> List[Dict]:
    """
    Scrape assignments for a single Canvas course URL.

    - course_url: e.g. https://canvas.illinois.edu/courses/66465
    - headless: run Chrome headless (default True for backend)
    - driver: reuse an existing driver (e.g. already logged in). If None, creates a new one.
    - profile_dir: optional path to Chrome user-data-dir with saved Canvas login (set CANVAS_PROFILE_DIR in env).

    Returns list of {id, title, url, due_text_raw}.
    Without login (profile or shared driver), the assignments page may show login and return empty list.
    """
    course_id = _parse_course_id_from_url(course_url)
    if not course_id:
        return []

    own_driver = False
    if driver is None:
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        if profile_dir:
            opts.add_argument(f"--user-data-dir={profile_dir}")
        if ChromeDriverManager:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=opts)
        else:
            driver = webdriver.Chrome(options=opts)
        own_driver = True

    try:
        return get_assignments_for_course(driver, course_id)
    finally:
        if own_driver:
            driver.quit()
