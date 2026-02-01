"""
Course Explorer Scraper
Scrapes enrolled courses from UIUC Course Explorer using Illinois SSO
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import json
import getpass
from datetime import datetime


def login_illinois_sso(driver, email, password):
    """
    Login through Illinois SSO (Microsoft)
    """
    print("🔐 Logging in via Illinois SSO...")
    
    try:
        # Wait for Microsoft login page
        email_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "loginfmt"))
        )
        print(f"   Entering email: {email}")
        email_field.clear()
        email_field.send_keys(email)
        email_field.send_keys(Keys.RETURN)
        
        time.sleep(2)
        
        # Enter password
        print("   Entering password...")
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "passwd"))
        )
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        
        time.sleep(3)
        
        # Handle "Stay signed in?" prompt
        try:
            print("   Handling 'Stay signed in?' prompt...")
            stay_signed_in = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "idBtn_Back"))
            )
            stay_signed_in.click()
        except:
            print("   (No prompt found, continuing...)")
        
        time.sleep(3)
        print("✅ SSO login completed!")
        
    except Exception as e:
        print(f"⚠️  SSO login issue: {e}")
        print("   Please complete login manually in the browser...")
        input("   Press Enter once you've logged in...")


def scrape_enrolled_courses(driver, term="2026", semester="spring"):
    """
    Scrape enrolled courses from Course Explorer
    """
    url = f"https://courses.illinois.edu/user/student/courselist/{term}/{semester}"
    print(f"\n📚 Navigating to Course Explorer: {url}")
    driver.get(url)
    
    time.sleep(3)
    
    # Check if we need to login
    if "login.microsoftonline.com" in driver.current_url or "shibboleth" in driver.current_url.lower():
        print("   Login required...")
        return None  # Will be handled by caller
    
    # Wait for the course table to load
    print("⏳ Waiting for course table...")
    try:
        table = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
        )
        print("✅ Course table found!")
    except Exception as e:
        print(f"❌ Could not find course table: {e}")
        return None
    
    # Extract course data
    courses = []
    
    try:
        # Find all rows in the table body
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        print(f"\n📊 Found {len(rows)} courses")
        
        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                
                if len(cells) >= 8:
                    # Extract course link and name
                    course_link = cells[0].find_element(By.TAG_NAME, "a") if cells[0].find_elements(By.TAG_NAME, "a") else None
                    course_name = course_link.text.strip() if course_link else cells[0].text.strip()
                    course_url = course_link.get_attribute("href") if course_link else None
                    
                    # Parse course name into department and number
                    course_parts = course_name.split()
                    department = course_parts[0] if course_parts else ""
                    number = course_parts[1] if len(course_parts) > 1 else ""
                    
                    course_data = {
                        "course": course_name,
                        "department": department,
                        "number": number,
                        "crn": cells[1].text.strip(),
                        "type": cells[2].text.strip(),
                        "section": cells[3].text.strip(),
                        "time": cells[4].text.strip(),
                        "days": cells[5].text.strip(),
                        "location": cells[6].text.strip(),
                        "instructor": cells[7].text.strip(),
                        "url": course_url
                    }
                    
                    courses.append(course_data)
                    print(f"   ✓ {course_name}: {course_data['type']} - {course_data['days']} {course_data['time']}")
                    
            except Exception as e:
                print(f"   ⚠️  Error parsing row: {e}")
                continue
        
        return courses
        
    except Exception as e:
        print(f"❌ Error extracting courses: {e}")
        return None


def main():
    print("=" * 60)
    print("🎓 COURSE EXPLORER SCRAPER")
    print("=" * 60)
    
    # Configuration
    email = input("\n📧 Enter your Illinois email (or press Enter for emilyk7@illinois.edu): ").strip()
    if not email:
        email = "emilyk7@illinois.edu"
    
    password = getpass.getpass("🔑 Enter your password: ")
    
    if not password:
        print("❌ Password cannot be empty!")
        return
    
    term = input("📅 Enter term year (default: 2026): ").strip() or "2026"
    semester = input("📅 Enter semester (spring/fall/summer, default: spring): ").strip() or "spring"
    
    # Initialize Safari WebDriver
    print("\n🌐 Initializing browser...")
    try:
        driver = webdriver.Safari()
        driver.maximize_window()
    except Exception as e:
        print(f"❌ Error initializing Safari: {e}")
        print("\n💡 To enable Safari WebDriver, run: sudo safaridriver --enable")
        return
    
    try:
        # Navigate to Course Explorer (will redirect to SSO)
        url = f"https://courses.illinois.edu/user/student/courselist/{term}/{semester}"
        print(f"\n📚 Navigating to: {url}")
        driver.get(url)
        
        time.sleep(2)
        
        # Login if needed
        if "login.microsoftonline.com" in driver.current_url or "shibboleth" in driver.current_url.lower():
            login_illinois_sso(driver, email, password)
            time.sleep(3)
        
        # Scrape courses
        courses = scrape_enrolled_courses(driver, term, semester)
        
        if courses:
            # Save to JSON
            output = {
                "user_email": email,
                "term": term,
                "semester": semester,
                "scraped_at": datetime.now().isoformat(),
                "course_count": len(courses),
                "courses": courses
            }
            
            filename = f"enrolled_courses_{term}_{semester}.json"
            with open(filename, "w") as f:
                json.dump(output, f, indent=2)
            
            print(f"\n✅ Successfully scraped {len(courses)} courses!")
            print(f"📄 Data saved to: {filename}")
            
            # Print summary
            print("\n📋 ENROLLED COURSES:")
            print("-" * 60)
            for course in courses:
                print(f"  • {course['course']} ({course['crn']})")
                print(f"    {course['type']} | {course['days']} {course['time']}")
                print(f"    {course['location']} | {course['instructor']}")
                print()
        else:
            print("\n❌ No courses found or scraping failed")
        
        print("\n🎉 Scraping complete!")
        input("⏸️  Press Enter to close the browser...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("⏸️  Press Enter to close the browser...")
    
    finally:
        driver.quit()
        print("🔚 Browser closed.")


if __name__ == "__main__":
    main()
