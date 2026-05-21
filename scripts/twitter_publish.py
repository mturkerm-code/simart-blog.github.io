import asyncio
from playwright.async_api import async_playwright
import json
import os
from datetime import datetime

# Credentials from GitHub Secrets
USERNAME = os.environ.get('TWITTER_USERNAME', 'eerman883')
PASSWORD = os.environ.get('TWITTER_PASSWORD', 'Erman123.')

screenshots_dir = "screenshots"
os.makedirs(screenshots_dir, exist_ok=True)

log_lines = []

def log(msg):
    print(msg)
    log_lines.append(f"{datetime.utcnow().isoformat()} | {msg}")

def save_screenshot(page, name):
    try:
        path = f"{screenshots_dir}/{name}_{datetime.now().strftime('%H%M%S')}.png"
        page.screenshot(path=path, full_page=False)
        log(f"📸 Screenshot: {path}")
        return path
    except Exception as e:
        log(f"⚠️ Screenshot failed: {e}")
        return None

def save_log():
    with open('publish_log.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))

async def main():
    log("🚀 Starting Twitter browser publish...")
    
    # Load tweets pool
    try:
        with open('data/tweets.json', 'r', encoding='utf-8') as f:
            tweets_data = json.load(f)
        tweets = tweets_data.get('tweets', [])
        log(f"✅ Loaded {len(tweets)} tweets from pool")
    except Exception as e:
        log(f"❌ Failed to load tweets.json: {e}")
        save_log()
        exit(1)
    
    if not tweets:
        log("❌ No tweets in pool")
        save_log()
        exit(1)
    
    # Load state (posted tweets tracking)
    state_file = 'publish_state.json'
    posted_ids = set()
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
            posted_ids = set(state.get('posted', []))
            log(f"📋 Previously posted: {len(posted_ids)} tweets")
    except:
        log("📝 New state file will be created")
    
    # Find unposted tweet
    unposted = [t for t in tweets if t.get('id') not in posted_ids]
    if not unposted:
        log("🔄 All tweets posted. Resetting rotation.")
        posted_ids = set()
        unposted = tweets[:]
    
    tweet = unposted[0]
    tweet_text = tweet.get('text', '')
    tweet_id = tweet.get('id', 0)
    
    log(f"📤 Selected tweet #{tweet_id}: {tweet_text[:80]}...")
    
    async with async_playwright() as p:
        # Launch browser with stealth
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-blink-features=AutomationControlled',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Hide automation
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            window.chrome = { runtime: {} };
        """)
        
        page = await context.new_page()
        
        # STEP 1: Navigate to Twitter login
        log("🌐 Step 1: Navigating to x.com/i/flow/login...")
        try:
            await page.goto("https://x.com/i/flow/login", wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)
            save_screenshot(page, "01_login_page")
            log(f"✅ Login page loaded. Title: {await page.title()}")
        except Exception as e:
            log(f"❌ Failed to load login page: {e}")
            save_screenshot(page, "01_login_error")
            await browser.close()
            save_log()
            exit(1)
        
        # STEP 2: Fill username
        log("📝 Step 2: Filling username...")
        try:
            # Wait for and fill username
            await page.wait_for_selector('input[autocomplete="username"], input[name="text"]', timeout=15000)
            await page.fill('input[autocomplete="username"], input[name="text"]', USERNAME)
            await page.wait_for_timeout(1000)
            save_screenshot(page, "02_username_filled")
            log(f"✅ Username filled: {USERNAME}")
            
            # Click Next
            next_btn = await page.query_selector('button:has-text("Next"), button:has-text("İleri"), button[type="submit"]')
            if next_btn:
                await next_btn.click()
                await page.wait_for_timeout(2000)
                save_screenshot(page, "03_after_next")
                log("✅ Clicked Next")
            else:
                log("⚠️ Next button not found, trying Enter key...")
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(2000)
        except Exception as e:
            log(f"❌ Username step failed: {e}")
            save_screenshot(page, "02_username_error")
            await browser.close()
            save_log()
            exit(1)
        
        # STEP 3: Fill password
        log("🔐 Step 3: Filling password...")
        try:
            await page.wait_for_selector('input[name="password"], input[type="password"]', timeout=15000)
            await page.fill('input[name="password"], input[type="password"]', PASSWORD)
            await page.wait_for_timeout(1000)
            save_screenshot(page, "04_password_filled")
            log("✅ Password filled")
            
            # Click Log in
            login_btn = await page.query_selector('button:has-text("Log in"), button:has-text("Giriş yap"), button[data-testid="LoginForm_Login_Button"]')
            if login_btn:
                await login_btn.click()
                log("✅ Clicked Log in")
            else:
                log("⚠️ Login button not found, trying Enter...")
                await page.keyboard.press('Enter')
            
            await page.wait_for_timeout(5000)
            save_screenshot(page, "05_after_login")
        except Exception as e:
            log(f"❌ Password step failed: {e}")
            save_screenshot(page, "04_password_error")
            await browser.close()
            save_log()
            exit(1)
        
        # STEP 4: Verify login
        log("🔍 Step 4: Verifying login...")
        current_url = page.url
        log(f"📍 Current URL: {current_url}")
        
        if "home" in current_url or "i/twitter" in current_url:
            log("✅ LOGIN SUCCESS - Home page detected!")
        elif "login" in current_url or "flow" in current_url:
            log("⚠️ Still on login/challenge page. Possible reCAPTCHA or verification needed.")
            # Check for challenge elements
            challenge = await page.query_selector('[data-testid="ocfEnterTextTextInput"], input[name="challenge_response"]')
            if challenge:
                log("❌ ACCOUNT CHALLENGE DETECTED - Manual intervention required (email/phone verification)")
                save_screenshot(page, "06_challenge")
                await browser.close()
                save_log()
                exit(1)
        else:
            log(f"⚠️ Unexpected URL: {current_url}")
        
        # STEP 5: Navigate to tweet composer
        log("✍️ Step 5: Opening tweet composer...")
        try:
            await page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(3000)
            save_screenshot(page, "07_composer")
            log("✅ Composer page loaded")
        except Exception as e:
            log(f"❌ Failed to open composer: {e}")
            save_screenshot(page, "07_composer_error")
            await browser.close()
            save_log()
            exit(1)
        
        # STEP 6: Write tweet
        log("📝 Step 6: Writing tweet...")
        try:
            # Find tweet text area
            tweet_box = await page.wait_for_selector('[data-testid="tweetTextarea_0"], div[role="textbox"], textarea', timeout=10000)
            if tweet_box:
                await tweet_box.fill(tweet_text)
                await page.wait_for_timeout(1000)
                save_screenshot(page, "08_tweet_written")
                log(f"✅ Tweet written: {tweet_text[:60]}...")
            else:
                log("❌ Tweet textarea not found")
                save_screenshot(page, "08_tweet_not_found")
                await browser.close()
                save_log()
                exit(1)
        except Exception as e:
            log(f"❌ Tweet writing failed: {e}")
            save_screenshot(page, "08_tweet_error")
            await browser.close()
            save_log()
            exit(1)
        
        # STEP 7: Submit tweet
        log("📤 Step 7: Submitting tweet...")
        try:
            post_btn = await page.query_selector('[data-testid="tweetButton"], button:has-text("Post"), button:has-text("Gönder")')
            if post_btn:
                await post_btn.click()
                await page.wait_for_timeout(3000)
                save_screenshot(page, "09_after_post")
                log("✅ Post button clicked")
                
                # Check if posted successfully
                current_url = page.url
                if "status" in current_url or "home" in current_url:
                    log("✅ TWEET POSTED SUCCESSFULLY!")
                    
                    # Update state
                    posted_ids.add(tweet_id)
                    with open(state_file, 'w') as f:
                        json.dump({
                            'posted': list(posted_ids),
                            'last_post': datetime.utcnow().isoformat(),
                            'last_tweet_id': tweet_id,
                            'last_tweet_text': tweet_text[:100]
                        }, f, indent=2)
                    log(f"📝 State updated. Total posted: {len(posted_ids)}")
                else:
                    log(f"⚠️ Unexpected URL after post: {current_url}")
                    save_screenshot(page, "09_post_unclear")
            else:
                log("❌ Post button not found")
                save_screenshot(page, "09_post_btn_missing")
                await browser.close()
                save_log()
                exit(1)
        except Exception as e:
            log(f"❌ Tweet submission failed: {e}")
            save_screenshot(page, "09_post_error")
            await browser.close()
            save_log()
            exit(1)
        
        await browser.close()
        log("\n✅ Browser publish completed successfully!")
    
    save_log()
    print("\n=== FULL LOG ===")
    print('\n'.join(log_lines))

if __name__ == "__main__":
    asyncio.run(main())
