import asyncio
import os
import random
import json
from datetime import datetime

# Bluesky AT Protocol - HTTP API ile post (önce API denenecek)
# Eğer API çalışmazsa Playwright fallback

async def post_to_bluesky_api(identifier, password, text):
    """Bluesky API ile post at (AT Protocol)"""
    import aiohttp
    
    # 1. Login
    async with aiohttp.ClientSession() as session:
        login_url = "https://bsky.social/xrpc/com.atproto.server.createSession"
        login_data = {"identifier": identifier, "password": password}
        
        async with session.post(login_url, json=login_data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status != 200:
                print(f"Login failed: {resp.status}")
                return None
            auth = await resp.json()
            access_jwt = auth.get("accessJwt")
            did = auth.get("did")
            handle = auth.get("handle")
            print(f"Login success: {handle} ({did})")
        
        # 2. Create post
        post_url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
        post_record = {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": datetime.utcnow().isoformat() + "Z"
        }
        post_data = {
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": post_record
        }
        
        headers = {"Authorization": f"Bearer {access_jwt}"}
        
        async with session.post(post_url, json=post_data, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status != 200:
                print(f"Post failed: {resp.status} - {await resp.text()}")
                return None
            result = await resp.json()
            uri = result.get("uri", "")
            print(f"Post success: {uri}")
            return uri

async def post_to_bluesky_browser(page, identifier, password, text):
    """Bluesky browser automation ile post at (Playwright fallback)"""
    
    # Login sayfasına git
    await page.goto("https://bsky.app")
    await page.wait_for_timeout(2000)
    
    # Sign in butonu varsa tıkla
    sign_in = await page.query_selector("text=Sign in")
    if sign_in:
        await sign_in.click()
        await page.wait_for_timeout(1500)
    
    # Login formu
    await page.fill("input[type='email']", identifier)
    await page.wait_for_timeout(500)
    await page.fill("input[type='password']", password)
    await page.wait_for_timeout(500)
    
    # Sign in butonu
    submit = await page.query_selector("button[type='submit']")
    if submit:
        await submit.click()
    else:
        # Alternatif: Enter tuşu
        await page.press("input[type='password']", "Enter")
    
    await page.wait_for_timeout(4000)
    
    # Composer aç
    new_post = await page.query_selector("text=New Post")
    if new_post:
        await new_post.click()
    else:
        # Alternatif selector
        await page.click("[aria-label*='new post' i], [aria-label*='compose' i]")
    
    await page.wait_for_timeout(1500)
    
    # Metin gir
    composer = await page.query_selector("textarea, [contenteditable='true']")
    if composer:
        await composer.fill(text)
    else:
        await page.keyboard.type(text, delay=random.randint(20, 80))
    
    await page.wait_for_timeout(1000)
    
    # Post butonu
    post_btn = await page.query_selector("text=Post")
    if post_btn:
        await post_btn.click()
    
    await page.wait_for_timeout(3000)
    
    # URL kontrol et - post atıldı mı?
    url = page.url
    if "/post/" in url:
        print(f"Browser post success: {url}")
        return url
    
    return None

async def main():
    identifier = os.environ.get("BLUESKY_IDENTIFIER", "eerman883@gmail.com")
    password = os.environ.get("BLUESKY_PASSWORD", "Erman123.")
    
    # Post havuzundan rastgele seç
    posts = [
        "Akıllı ev kurarken en çok karşılaştığım soru: \"Hangi robot süpürge?\" Ben 6 ayda 6 marka test ettim. Sonuç: 3000-4000 TL bandında yerli üretim + Türkçe destek kritik. Şımart'ın 2700Pa emiş gücü ve 48 saat servisi beni ikna etti. Detaylı karşılaştırma blogumda.",
        "2026'da akıllı ev güvenliği artık \"opsiyonel\" değil. Kamera + robot süpürge + akıllı priz üçlüsü, evinizi hem konforlu hem güvenli yapıyor. Yerli markaların Türkçe uygulama ve yerinde servis avantajı yabancılara karşı büyük fark. Deneyimlerim ve karşılaştırmalar.",
        "Robot süpürge batarya ömrü: 6 marka, 6 ay test. %8 kapasite kaybıyla en dayanıklı ikinci olan model fiyatı en düşük üçüncüydü. Bu test sonuçları bana \"pahalı = iyi\" algısını sorgulattı. Detaylı analiz ve bütçe tablosu.",
        "3 yıllık robot süpürge vs elektrikli süpürge maliyet analizi yaptım. Robot: 3200 TL başlangıç + 300 TL/yıl sarf. Elektrikli: 800 TL + zaman maliyeti. 3. yılda robot kendini amorti ediyor. Üstelik yerli marka alınca yedek parça ve servis sorunu da kalmıyor.",
        "İstanbul'da 110m² evde akıllı ev sistemleri kurdum. 8 marka güvenlik kamerası, 6 robot süpürge, 4 akıllı priz test ettim. Hangisi stabil, hangisi uygulaması Türkçe, hangisinin servisi 48 saatte geliyor? Hepsi blogda, karşılaştırma tablolarıyla.",
    ]
    
    text = random.choice(posts)
    
    print(f"[{datetime.now().isoformat()}] Bluesky post başlıyor...")
    print(f"Identifier: {identifier}")
    print(f"Text length: {len(text)} chars")
    
    # Önce API dene
    try:
        result = await post_to_bluesky_api(identifier, password, text)
        if result:
            print(f"✅ API post success: {result}")
            return
    except Exception as e:
        print(f"API failed: {e}")
    
    # Fallback: Browser automation
    print("API failed, trying browser automation...")
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            result = await post_to_bluesky_browser(page, identifier, password, text)
            if result:
                print(f"✅ Browser post success: {result}")
            else:
                print("❌ Browser post failed")
            
            await browser.close()
    except ImportError:
        print("Playwright not installed, skipping browser fallback")
    except Exception as e:
        print(f"Browser error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
