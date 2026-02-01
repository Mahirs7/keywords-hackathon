from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import getpass
from datetime import datetime

def login_to_campuswire(driver, email, password):
    """
    Log into Campuswire with email/password
    """
    print("🌐 Navigating to Campuswire login...")
    driver.get("https://campuswire.com/signin")
    
    time.sleep(3)
    
    try:
        # Find email input - using placeholder text
        print(f"✍️  Entering email: {email}")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email' or @type='email']"))
        )
        email_field.clear()
        email_field.send_keys(email)
        
        time.sleep(1)
        
        # Find password input
        print("🔑 Entering password...")
        password_field = driver.find_element(By.XPATH, "//input[@placeholder='Password' or @type='password']")
        password_field.clear()
        password_field.send_keys(password)
        
        time.sleep(1)
        
        # Click Sign in button
        print("🚀 Clicking Sign in...")
        sign_in_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]")
        sign_in_btn.click()
        
        time.sleep(5)
        
        # Check if login was successful
        if "signin" not in driver.current_url.lower():
            print("✅ Login successful!")
        else:
            print(f"⚠️  May need additional verification...")
            print(f"   Current URL: {driver.current_url}")
            input("   Press Enter once you've completed login in the browser...")
            
    except Exception as e:
        print(f"⚠️  Login process encountered an issue: {e}")
        print("   Please complete login manually in the browser...")
        input("   Press Enter once you've logged in...")

def scrape_feed(driver, feed_url, max_posts=50):
    """
    Scrape posts from a Campuswire feed
    """
    print(f"\n📰 Navigating to feed: {feed_url}")
    driver.get(feed_url)
    
    time.sleep(3)
    
    posts = []
    
    try:
        # Wait for feed to load
        print("⏳ Waiting for feed to load...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='feed'], [class*='post'], [class*='thread']"))
        )
        print("✅ Feed loaded!")
        
        # Scroll to load more posts
        print("📜 Scrolling to load more posts...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 10
        
        while scroll_attempts < max_scrolls and len(posts) < max_posts:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Check for new content
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
            else:
                scroll_attempts = 0
            last_height = new_height
            
            # Count posts
            current_posts = driver.find_elements(By.CSS_SELECTOR, "[class*='post-item'], [class*='thread-item'], [class*='feed-item'], article")
            print(f"   Found {len(current_posts)} items so far...")
            
            if len(current_posts) >= max_posts:
                break
        
        # Now scrape the posts
        print("\n📊 Extracting post data...")
        
        # Get page source for parsing
        page_source = driver.page_source
        
        # Try different selectors to find posts
        post_elements = []
        selectors_to_try = [
            "[class*='post-item']",
            "[class*='thread-item']",
            "[class*='feed-item']",
            "[class*='FeedItem']",
            "article",
            "[data-testid*='post']",
            ".post",
            ".thread"
        ]
        
        for selector in selectors_to_try:
            post_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if post_elements:
                print(f"   Found {len(post_elements)} posts using selector: {selector}")
                break
        
        if not post_elements:
            # Fallback: try to extract from any list-like structure
            print("   Using fallback extraction method...")
            post_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed')]//div[contains(@class, 'item') or contains(@class, 'post')]")
        
        for i, post_el in enumerate(post_elements[:max_posts], 1):
            try:
                post_data = {
                    'index': i,
                    'text': post_el.text.strip(),
                    'html': post_el.get_attribute('innerHTML')[:500] if post_el.get_attribute('innerHTML') else ''
                }
                
                # Try to extract specific fields
                try:
                    title_el = post_el.find_element(By.CSS_SELECTOR, "h1, h2, h3, h4, [class*='title'], [class*='subject']")
                    post_data['title'] = title_el.text.strip()
                except:
                    pass
                
                try:
                    author_el = post_el.find_element(By.CSS_SELECTOR, "[class*='author'], [class*='user'], [class*='name']")
                    post_data['author'] = author_el.text.strip()
                except:
                    pass
                
                try:
                    date_el = post_el.find_element(By.CSS_SELECTOR, "[class*='date'], [class*='time'], [class*='ago']")
                    post_data['date'] = date_el.text.strip()
                except:
                    pass
                
                try:
                    category_el = post_el.find_element(By.CSS_SELECTOR, "[class*='category'], [class*='tag'], [class*='label']")
                    post_data['category'] = category_el.text.strip()
                except:
                    pass
                
                # Get links
                links = post_el.find_elements(By.TAG_NAME, 'a')
                post_data['links'] = [{'text': l.text, 'href': l.get_attribute('href')} for l in links if l.get_attribute('href')]
                
                posts.append(post_data)
                print(f"   Post {i}: {post_data.get('title', post_data['text'][:50])}...")
                
            except Exception as e:
                print(f"   ⚠️  Error extracting post {i}: {e}")
        
        return {
            'feed_url': feed_url,
            'posts': posts,
            'total_posts': len(posts),
            'scraped_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error scraping feed: {e}")
        return None

def scrape_post_details(driver, post_url):
    """
    Scrape full details of a single post including comments
    """
    print(f"\n📄 Scraping post: {post_url}")
    driver.get(post_url)
    time.sleep(2)
    
    try:
        post_data = {
            'url': post_url,
            'scraped_at': datetime.now().isoformat()
        }
        
        # Wait for post to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Extract main post content
        try:
            title = driver.find_element(By.CSS_SELECTOR, "h1, h2, [class*='title']")
            post_data['title'] = title.text.strip()
        except:
            pass
        
        try:
            content = driver.find_element(By.CSS_SELECTOR, "[class*='content'], [class*='body'], article")
            post_data['content'] = content.text.strip()
        except:
            pass
        
        # Extract comments/answers
        comments = []
        comment_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='comment'], [class*='answer'], [class*='reply']")
        
        for j, comment_el in enumerate(comment_elements, 1):
            try:
                comment_data = {
                    'index': j,
                    'text': comment_el.text.strip()
                }
                comments.append(comment_data)
            except:
                pass
        
        post_data['comments'] = comments
        post_data['comment_count'] = len(comments)
        
        return post_data
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    print("="*60)
    print("📚 CAMPUSWIRE SCRAPER")
    print("="*60)
    
    # Configuration
    email = "mahirs2@illinois.edu"
    feed_url = "https://campuswire.com/c/GCE159BBC/feed"
    
    print(f"\n📧 Email: {email}")
    print(f"📰 Feed URL: {feed_url}")
    
    # Get password
    password = getpass.getpass("\n🔑 Enter your password: ")
    
    if not password:
        print("❌ Password cannot be empty!")
        return
    
    # Initialize Safari WebDriver
    print("\n🌐 Initializing Safari...")
    try:
        driver = webdriver.Safari()
        driver.maximize_window()
    except Exception as e:
        print(f"❌ Error initializing Safari: {e}")
        print("\n💡 To enable Safari WebDriver, run in Terminal:")
        print("   sudo safaridriver --enable")
        return
    
    try:
        # Login to Campuswire
        login_to_campuswire(driver, email, password)
        
        # Navigate directly to the feed (might already be logged in via SSO)
        print(f"\n📰 Going to feed URL: {feed_url}")
        driver.get(feed_url)
        time.sleep(3)
        
        # Check if we need to login
        if "login" in driver.current_url.lower() or "signin" in driver.current_url.lower():
            print("⚠️  Still on login page, please complete login manually...")
            input("   Press Enter once you've logged in...")
        
        # Scrape the feed
        data = scrape_feed(driver, feed_url, max_posts=100)
        
        if data:
            # Save to JSON file
            output_file = f"campuswire_feed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n✅ Data saved to: {output_file}")
            print(f"📊 Total posts scraped: {data['total_posts']}")
        else:
            print("\n❌ No data scraped")
        
        # Keep browser open for inspection
        print("\n🎉 Scraping complete!")
        print("🔍 Browser will stay open. Check the data and close manually.")
        input("\n⏸️  Press Enter to close the browser...")
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        print("🔍 Browser will stay open for debugging.")
        input("\n⏸️  Press Enter to close the browser...")
    
    finally:
        driver.quit()
        print("🔚 Browser closed.")

if __name__ == "__main__":
    main()
