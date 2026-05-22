import os
import time
import random
from datetime import datetime

# Tumblr Auto Post - Playwright Browser Automation
# Tumblr'a gir, login ol, post at. Her seferinde browser acilir.

async def post_to_tumblr(page, email, password, title, content, tags):
    """Tumblr'da post at"""
    
    # 1. Login sayfasına git
    await page.goto("https://www.tumblr.com/login")
    await page.wait_for_timeout(3000)
    
    # 2. Email ve password gir
    await page.fill("input[name='email']", email)
    await page.wait_for_timeout(random.randint(500, 1000))
    await page.fill("input[name='password']", password)
    await page.wait_for_timeout(random.randint(500, 1000))
    
    # 3. Login butonuna tıkla
    await page.click("button[type='submit']")
    await page.wait_for_timeout(5000)
    
    # 4. Post composer aç
    await page.goto("https://www.tumblr.com/new/text")
    await page.wait_for_timeout(3000)
    
    # 5. Başlık gir
    title_input = await page.query_selector("[placeholder*='Title' i], [aria-label*='title' i]")
    if title_input:
        await title_input.fill(title)
    else:
        # Alternatif: ilk contenteditable veya textarea
        await page.keyboard.type(title, delay=random.randint(30, 70))
    
    await page.wait_for_timeout(1000)
    
    # 6. İçerik gir
    content_area = await page.query_selector("[contenteditable='true']")
    if content_area:
        await content_area.fill(content)
    else:
        await page.keyboard.press("Tab")
        await page.keyboard.type(content, delay=random.randint(20, 50))
    
    await page.wait_for_timeout(1500)
    
    # 7. Tag ekle (varsa)
    if tags:
        tag_input = await page.query_selector("[placeholder*='tag' i], [aria-label*='tag' i]")
        if tag_input:
            for tag in tags[:5]:  # max 5 tag
                await tag_input.fill(tag)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(500)
    
    await page.wait_for_timeout(2000)
    
    # 8. Post butonuna tıkla
    post_btn = await page.query_selector("text=Post, button[data-testid*='post' i]")
    if post_btn:
        await post_btn.click()
    else:
        await page.keyboard.press("Control+Enter")
    
    await page.wait_for_timeout(4000)
    
    # 9. URL kontrol et
    url = page.url
    if "/post/" in url or "/blog/" in url:
        print(f"Post success: {url}")
        return url
    
    return None

async def main():
    email = os.environ.get("TUMBLR_EMAIL", "eerman883@gmail.com")
    password = os.environ.get("TUMBLR_PASSWORD", "Erman123.")
    
    posts = [
        {
            "title": "2026 Akıllı Ev Başlangıç Rehberi",
            "content": "Akilli ev kurmak sandigindan daha kolay. 3000 TL ile robot supurge + akilli priz + guvenlik kamera baslangici yapilabilir. Ben 6 ayda kurdum, detaylar blogumda. Yerli markalarin Turkce destek avantaji kritik.",
            "tags": ["akilli ev", "robot supurge", "teknoloji", "turkey"]
        },
        {
            "title": "Robot Supurge Alirken 10 Kritik Ozellik",
            "content": "Emis gucu, batarya, haritalama, Turkce uygulama... 6 marka test ettim. Fiyat/performans olarak yerli uretim on planda cikiyor. LIDAR + 2700Pa + 5200mAh kombinasyonu ideal. 2 yil garanti + 48 saat servis sart.",
            "tags": ["robot supurge", "teknoloji", "rehber"]
        },
    ]
    
    import random
    post = random.choice(posts)
    
    print(f"[{datetime.now().isoformat()}] Tumblr post basliyor...")
    
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        result = await post_to_tumblr(page, email, password, post["title"], post["content"], post["tags"])
        
        if result:
            print(f"Basariyla yayinlandi: {result}")
        else:
            print("Yayinlanamadi.")
        
        await browser.close()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
