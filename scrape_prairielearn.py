from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import json
import getpass
from datetime import datetime

def login_to_prairielearn(driver, email, password):
    """
    Log into PrairieLearn using Illinois SAML SSO
    """
    print("🌐 Navigating to PrairieLearn...")
    driver.get("https://us.prairielearn.com")
    
    time.sleep(2)
    
    try:
        # Step 1: Click on University of Illinois Urbana-Champaign (UIUC) button
        print("🏫 Looking for University of Illinois login button...")
        
        # Find the UIUC institution button (institution/3)
        uiuc_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/pl/auth/institution/3/saml/login')]"))
        )
        print("   ✓ Found UIUC button, clicking...")
        uiuc_button.click()
        
        time.sleep(3)
        
        # Step 2: Illinois SSO - Enter email (NetID@illinois.edu)
        print(f"✍️  Entering email: {email}")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "loginfmt"))
        )
        email_field.send_keys(email)
        email_field.send_keys(Keys.RETURN)
        
        time.sleep(2)
        
        # Step 3: Enter password
        print("🔑 Entering password...")
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "passwd"))
        )
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        
        time.sleep(3)
        
        # Step 4: Handle "Stay signed in?" prompt if it appears
        try:
            print("⏭️  Handling 'Stay signed in?' prompt...")
            stay_signed_in = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "idBtn_Back"))
            )
            stay_signed_in.click()
        except:
            print("   (No prompt found, continuing...)")
        
        # Wait for redirect back to PrairieLearn
        print("⏳ Waiting for login to complete...")
        time.sleep(5)
        
        # Check if we're logged in
        if "prairielearn" in driver.current_url.lower():
            print("✅ Login successful!")
        else:
            print(f"⚠️  Current URL: {driver.current_url}")
            print("   You may need to complete additional verification (Duo, etc.)")
            input("   Press Enter once you've completed login in the browser...")
        
    except Exception as e:
        print(f"⚠️  Login process encountered an issue: {e}")
        print("   Please complete login manually in the browser...")
        input("   Press Enter once you've logged in...")

def scrape_assessments(driver, course_instance_id):
    """
    Scrape assessments from PrairieLearn course instance
    """
    # Navigate to assessments page
    url = f"https://us.prairielearn.com/pl/course_instance/{course_instance_id}/assessments"
    print(f"\n📄 Navigating to assessments page...")
    print(f"   URL: {url}")
    driver.get(url)
    
    # Wait for the table to load
    print("⏳ Waiting for assessments table to load...")
    try:
        table = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-sm.table-hover"))
        )
        print("✅ Table found!")
    except Exception as e:
        print(f"❌ Could not find table: {e}")
        print("Current page source (first 1000 chars):")
        print(driver.page_source[:1000])
        return None
    
    # Extract table data
    assessments = []
    
    try:
        # Find all rows in tbody
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        print(f"\n📊 Found {len(rows)} assessment rows")
        
        for i, row in enumerate(rows, 1):
            try:
                # Extract all cells
                cells = row.find_elements(By.TAG_NAME, "td")
                
                assessment_data = {
                    'row_number': i,
                    'cells': [],
                    'raw_text': row.text
                }
                
                # Extract text from each cell
                for j, cell in enumerate(cells):
                    cell_data = {
                        'index': j,
                        'text': cell.text.strip(),
                        'html': cell.get_attribute('innerHTML')[:200]  # First 200 chars
                    }
                    assessment_data['cells'].append(cell_data)
                
                # Try to find links
                links = row.find_elements(By.TAG_NAME, "a")
                assessment_data['links'] = []
                for link in links:
                    assessment_data['links'].append({
                        'text': link.text.strip(),
                        'href': link.get_attribute('href')
                    })
                
                assessments.append(assessment_data)
                print(f"   Row {i}: {assessment_data['raw_text'][:100]}...")
                
            except Exception as e:
                print(f"   ⚠️  Error extracting row {i}: {e}")
        
        # Also get the table headers
        headers = []
        try:
            header_cells = table.find_elements(By.CSS_SELECTOR, "thead th")
            for cell in header_cells:
                headers.append(cell.text.strip())
            print(f"\n📋 Headers: {headers}")
        except:
            print("⚠️  Could not extract headers")
        
        return {
            'headers': headers,
            'assessments': assessments,
            'scraped_at': datetime.now().isoformat(),
            'course_instance_id': course_instance_id
        }
        
    except Exception as e:
        print(f"❌ Error extracting table data: {e}")
        return None

def main():
    print("="*60)
    print("🎓 PRAIRIELEARN ASSESSMENTS SCRAPER")
    print("="*60)
    
    # Configuration
    email = "mahirs2@illinois.edu"
    course_instance_id = "206336"
    
    print(f"\n📧 Email: {email}")
    print(f"📚 Course Instance ID: {course_instance_id}")
    
    # Get password
    password = getpass.getpass("\n🔑 Enter your Illinois password: ")
    
    if not password:
        print("❌ Password cannot be empty!")
        return
    
    # Initialize WebDriver (try Chrome, then Safari)
    print("\n🌐 Initializing browser...")
    driver = None
    
    # Try Chrome first with custom path - let Selenium auto-manage driver
    try:
        print("   Trying Chrome...")
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.binary_location = "/Applications/Google Chrome 3.app/Contents/MacOS/Google Chrome"
        
        # Let Selenium Manager handle the driver automatically
        driver = webdriver.Chrome(options=chrome_options)
        print("   ✓ Using Chrome!")
    except Exception as e:
        print(f"   ✗ Chrome not available: {e}")
        
        # Try Safari
        try:
            print("   Trying Safari...")
            driver = webdriver.Safari()
            print("   ✓ Using Safari!")
        except Exception as e2:
            print(f"   ✗ Safari error: {e2}")
            print("\n💡 To enable Safari WebDriver, run in Terminal:")
            print("   sudo safaridriver --enable")
            return
    
    driver.maximize_window()
    
    try:
        # Login to PrairieLearn
        login_to_prairielearn(driver, email, password)
        
        # Scrape assessments
        data = scrape_assessments(driver, course_instance_id)
        
        if data:
            # Save to JSON file
            output_file = f"assessments_{course_instance_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n✅ Data saved to: {output_file}")
            print(f"📊 Total assessments: {len(data['assessments'])}")
        else:
            print("\n❌ No data scraped")
        
        # Keep browser open for inspection
        print("\n🎉 Scraping complete!")
        print("🔍 Browser will stay open. Check the data and close manually.")
        input("\n⏸️  Press Enter to close the browser...")
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        print("🔍 Browser will stay open for debugging.")
        input("\n⏸️  Press Enter to close the browser...")
    
    finally:
        driver.quit()
        print("🔚 Browser closed.")

if __name__ == "__main__":
    main()
