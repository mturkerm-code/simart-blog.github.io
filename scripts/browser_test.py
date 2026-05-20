import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

# Credentials
USERNAME = "eerman883"
PASSWORD = "Erman123."

screenshots_dir = "screenshots"
os.makedirs(screenshots_dir, exist_ok=True)

def save_screenshot(page, name):
    path = f"{screenshots_dir}/{name}_{datetime.now().strftime('%H%M%S')}.png"
    page.screenshot(path=path, full_page=True)
    print(f"📸 Screenshot saved: {path}")
    return path

async def main():
    async with async_playwright() as p:
        # Launch browser with stealth options
        browser = await p.chromium.launch(
            headless=True,  # GitHub Actions'ta headless zorunlu
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Inject script to hide automation
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            window.chrome = { runtime: {} };
        """)
        
        page = await context.new_page()
        
        print("🌐 Navigating to x.com...")
        try:
            await page.goto("https://x.com", wait_until="domcontentloaded", timeout=15000)
            save_screenshot(page, "01_x_home")
            print(f"✅ x.com loaded. Title: {await page.title()}")
        except Exception as e:
            print(f"❌ Failed to load x.com: {e}")
            save_screenshot(page, "01_x_home_error")
            await browser.close()
            return
        
        # Check if login button exists
        print("🔍 Looking for login button...")
        login_selectors = [
            'a[href="/login"]',
            '[data-testid="loginButton"]',
            'a:has-text("Sign in")',
            'a:has-text("Giriş yap")',
        ]
        
        login_found = False
        for selector in login_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                print(f"✅ Found login element: {selector}")
                login_found = True
                break
            except:
                continue
        
        if not login_found:
            print("⚠️ No login button found. Screenshot saved.")
            save_screenshot(page, "02_no_login_button")
        
        # Try to navigate to login page directly
        print("🔄 Trying direct login URL...")
        try:
            await page.goto("https://x.com/login", wait_until="domcontentloaded", timeout=15000)
            save_screenshot(page, "03_login_page")
            print(f"✅ Login page loaded. Title: {await page.title()}")
        except Exception as e:
            print(f"❌ Failed to load login page: {e}")
            save_screenshot(page, "03_login_error")
            await browser.close()
            return
        
        # Try to fill login form
        print("📝 Attempting to fill login form...")
        try:
            # Username field
            await page.wait_for_selector('input[autocomplete="username"], input[name="text"], input[name="username"]', timeout=10000)
            username_field = await page.query_selector('input[autocomplete="username"], input[name="text"], input[name="username"]')
            if username_field:
                await username_field.fill(USERNAME)
                print(f"✅ Filled username: {USERNAME}")
                save_screenshot(page, "04_username_filled")
            
            # Next button
            next_button = await page.query_selector('button:has-text("Next"), button:has-text("İleri"), button[type="submit"]')
            if next_button:
                await next_button.click()
                print("✅ Clicked Next")
                await page.wait_for_timeout(2000)
                save_screenshot(page, "05_after_next")
            
            # Password field
            await page.wait_for_selector('input[name="password"], input[type="password"]', timeout=10000)
            password_field = await page.query_selector('input[name="password"], input[type="password"]')
            if password_field:
                await password_field.fill(PASSWORD)
                print("✅ Filled password")
                save_screenshot(page, "06_password_filled")
            
            # Login button
            login_button = await page.query_selector('button:has-text("Log in"), button:has-text("Giriş yap"), button[data-testid="LoginForm_Login_Button"]')
            if login_button:
                await login_button.click()
                print("✅ Clicked Login")
                await page.wait_for_timeout(5000)
                save_screenshot(page, "07_after_login")
            
            # Check result
            current_url = page.url
            print(f"📍 Current URL after login: {current_url}")
            
            if "home" in current_url or "eerman883" in current_url:
                print("✅ LOGIN SUCCESS! Home page detected.")
            elif "challenge" in current_url or "login" in current_url:
                print("⚠️ Login challenge or still on login page. Possible reCAPTCHA or verification needed.")
            else:
                print(f"⚠️ Unexpected URL: {current_url}")
                
        except Exception as e:
            print(f"❌ Login form interaction failed: {e}")
            save_screenshot(page, "08_login_form_error")
        
        # Final screenshot
        save_screenshot(page, "99_final")
        
        await browser.close()
        print("\n✅ Browser test completed. Check screenshots in artifacts.")

if __name__ == "__main__":
    asyncio.run(main())
