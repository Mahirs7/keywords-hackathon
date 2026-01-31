from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import getpass
import os

def login_to_outlook(email, password):
    """
    Automate login to Illinois Outlook account with visual browser interaction
    """
    print("🌐 Initializing browser...")
    
    # Try Safari first (requires enabling: sudo safaridriver --enable)
    driver = None
    
    # Try Safari
    try:
        print("   Trying Safari...")
        driver = webdriver.Safari()
        print("   ✓ Using Safari!")
    except Exception as e:
        print(f"   ✗ Safari error: {e}")
        print("\n💡 To enable Safari WebDriver, run in Terminal:")
        print("   sudo safaridriver --enable")
        print("   (requires your Mac password)")
        return
    
    driver.maximize_window()
    
    try:
        # Navigate to Outlook
        print("📧 Navigating to Outlook...")
        driver.get("https://outlook.office365.com")
        
        # Wait and enter email
        print(f"✍️  Entering email: {email}")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "loginfmt"))
        )
        email_field.send_keys(email)
        email_field.send_keys(Keys.RETURN)
        
        time.sleep(2)
        
        # Wait and enter password
        print("🔐 Entering password...")
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "passwd"))
        )
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        
        time.sleep(2)
        
        # Handle "Stay signed in?" prompt
        try:
            print("⏭️  Handling 'Stay signed in?' prompt...")
            stay_signed_in = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "idBtn_Back"))
            )
            stay_signed_in.click()
        except:
            print("   (No prompt found, continuing...)")
        
        # Wait for Outlook to load
        print("⏳ Waiting for Outlook to load...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        time.sleep(3)
        
        # Check if login was successful by looking for common Outlook elements
        if "outlook" in driver.current_url.lower():
            print("\n✅ Successfully logged into Outlook!")
            print(f"📍 Current URL: {driver.current_url}")
            print("\n🎉 Browser will stay open. Close it manually when done.")
            
            # Keep browser open
            input("\n⏸️  Press Enter to close the browser...")
        else:
            print("\n⚠️  Login may have failed or requires additional verification.")
            print(f"📍 Current URL: {driver.current_url}")
            input("\n⏸️  Press Enter to close the browser...")
            
    except Exception as e:
        print(f"\n❌ Error during login: {e}")
        print("🔍 Browser will stay open for debugging. Close it manually.")
        input("\n⏸️  Press Enter to close the browser...")
    
    finally:
        driver.quit()
        print("🔚 Browser closed.")


def main():
    print("="*60)
    print("📬 OUTLOOK LOGIN AUTOMATION")
    print("="*60)
    
    # Email is pre-filled
    email = "mahirs2@illinois.edu"
    print(f"\n📧 Email: {email}")
    
    # Get password securely (won't be displayed)
    password = getpass.getpass("🔑 Enter your password: ")
    
    if not password:
        print("❌ Password cannot be empty!")
        return
    
    print("\n🚀 Starting login process...\n")
    login_to_outlook(email, password)


if __name__ == "__main__":
    main()
