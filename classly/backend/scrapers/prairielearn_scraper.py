"""
PrairieLearn scraper - fetches assessments for a course instance.
Uses Selenium to handle authentication and scrape assessment tables.
"""

import json
import re
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
from urllib.parse import urlparse, urljoin

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

PRAIRIELEARN_BASE_URL = "https://us.prairielearn.com"


def _parse_course_instance_id(url: str) -> Optional[str]:
    """Extract course_instance_id from URL like https://us.prairielearn.com/pl/course_instance/206336/assessments"""
    path = urlparse(url).path
    m = re.search(r'/course_instance/(\d+)', path)
    return m.group(1) if m else None


def _parse_due_date(due_text: str) -> Optional[str]:
    """Parse due date text like '100% until 23:59, Tue, Feb 3' into ISO format."""
    # Extract time and date parts
    match = re.search(r'(\d{1,2}:\d{2}),\s*(\w+),\s*(\w+)\s+(\d+)', due_text)
    if match:
        time_str, day_name, month_str, day = match.groups()
        # For now, return the raw text - LLM will clean it up
        return due_text
    return due_text if due_text else None


def scrape_prairielearn_assessments(
    course_url: str,
    *,
    headless: bool = True,
    driver: Optional[webdriver.Chrome] = None,
    profile_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Scrape assessments from a PrairieLearn course instance.
    
    Args:
        course_url: URL like https://us.prairielearn.com/pl/course_instance/206336/assessments
        headless: Run Chrome in headless mode
        driver: Reuse an existing driver (with auth session)
        profile_dir: Path to Chrome profile with saved login
    
    Returns:
        Dict with headers, assessments list, and metadata
    """
    course_instance_id = _parse_course_instance_id(course_url)
    if not course_instance_id:
        return {"error": "Could not parse course_instance_id from URL", "assessments": []}
    
    # Ensure URL ends with /assessments
    if not course_url.rstrip('/').endswith('/assessments'):
        course_url = course_url.rstrip('/') + '/assessments'
    
    own_driver = False
    if driver is None:
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        if profile_dir:
            opts.add_argument(f"--user-data-dir={profile_dir}")
        
        if ChromeDriverManager:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=opts)
        else:
            driver = webdriver.Chrome(options=opts)
        own_driver = True
    
    try:
        driver.get(course_url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table, .alert, body"))
        )
        time.sleep(1)  # Let dynamic content load
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Check if we hit a login page
        if "login" in driver.current_url.lower() or soup.select_one('form[action*="login"]'):
            return {
                "error": "Authentication required - please log in to PrairieLearn",
                "assessments": [],
                "course_instance_id": course_instance_id
            }
        
        # Find the assessments table
        table = soup.select_one('table.table')
        if not table:
            return {
                "error": "Could not find assessments table",
                "assessments": [],
                "course_instance_id": course_instance_id
            }
        
        # Parse headers
        headers = []
        header_row = table.select_one('thead tr')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.select('th')]
        
        # Parse assessment rows
        assessments = []
        rows = table.select('tbody tr')
        
        current_week = None
        for row in rows:
            cells = row.select('td')
            
            # Check if this is a week separator row
            if len(cells) == 1 or row.select_one('th[colspan]'):
                week_text = row.get_text(strip=True)
                if week_text:
                    current_week = week_text
                continue
            
            if len(cells) < 2:
                continue
            
            # Extract assessment data
            assessment = {
                "week": current_week,
                "cells": [],
                "links": []
            }
            
            for idx, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                assessment["cells"].append({
                    "index": idx,
                    "text": cell_text,
                    "html": str(cell)[:200]  # Truncate HTML
                })
                
                # Extract links
                for link in cell.select('a[href]'):
                    href = link.get('href', '')
                    if href.startswith('/'):
                        href = urljoin(PRAIRIELEARN_BASE_URL, href)
                    assessment["links"].append({
                        "text": link.get_text(strip=True),
                        "href": href
                    })
            
            # Extract key fields based on typical PrairieLearn structure
            if len(assessment["cells"]) >= 4:
                assessment["label"] = assessment["cells"][0]["text"]  # A1, POGIL1, etc.
                assessment["title"] = assessment["cells"][1]["text"]  # Assessment name
                assessment["due_info"] = assessment["cells"][2]["text"]  # Due date/credit info
                assessment["status"] = assessment["cells"][3]["text"]  # Score/status
            
            assessments.append(assessment)
        
        return {
            "headers": headers,
            "assessments": assessments,
            "course_instance_id": course_instance_id,
            "scraped_at": datetime.now().isoformat(),
            "source_url": course_url
        }
        
    finally:
        if own_driver:
            driver.quit()


def scrape_prairielearn_with_cookies(
    course_url: str,
    cookies: List[Dict[str, str]],
    headless: bool = True
) -> Dict[str, Any]:
    """
    Scrape PrairieLearn using provided cookies for authentication.
    
    Args:
        course_url: The course assessments URL
        cookies: List of cookie dicts with 'name', 'value', 'domain' keys
        headless: Run in headless mode
    
    Returns:
        Scraped assessment data
    """
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    
    if ChromeDriverManager:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)
    else:
        driver = webdriver.Chrome(options=opts)
    
    try:
        # First visit the domain to set cookies
        driver.get(PRAIRIELEARN_BASE_URL)
        time.sleep(1)
        
        # Add cookies
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"Failed to add cookie: {e}")
        
        # Now scrape with authentication
        return scrape_prairielearn_assessments(course_url, driver=driver, headless=headless)
        
    finally:
        driver.quit()
