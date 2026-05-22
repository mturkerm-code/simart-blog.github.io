import os
import requests
import json
from datetime import datetime
import random

# Bluesky Auto Post - AT Protocol HTTP API
# API key gerekmez, direkt email/sifre ile calisir

class BlueskyPoster:
    def __init__(self, identifier, password):
        self.identifier = identifier
        self.password = password
        self.access_jwt = None
        self.did = None
        self.handle = None
        self.service_url = "https://bsky.social"
    
    def login(self):
        """Login ve token al"""
        url = f"{self.service_url}/xrpc/com.atproto.server.createSession"
        data = {"identifier": self.identifier, "password": self.password}
        
        resp = requests.post(url, json=data, timeout=30)
        if resp.status_code != 200:
            print(f"Login hatasi: {resp.status_code}")
            print(resp.text[:500])
            return False
        
        auth = resp.json()
        self.access_jwt = auth.get("accessJwt")
        self.did = auth.get("did")
        self.handle = auth.get("handle")
        print(f"Login basarili: {self.handle}")
        return True
    
    def post(self, text):
        """Post at"""
        if not self.access_jwt:
            if not self.login():
                return None
        
        url = f"{self.service_url}/xrpc/com.atproto.repo.createRecord"
        
        post_record = {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": datetime.utcnow().isoformat() + "Z"
        }
        
        payload = {
            "repo": self.did,
            "collection": "app.bsky.feed.post",
            "record": post_record
        }
        
        headers = {"Authorization": f"Bearer {self.access_jwt}"}
        
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            uri = result.get("uri", "")
            print(f"Post basarili: {uri}")
            return uri
        else:
            print(f"Post hatasi: {resp.status_code}")
            print(resp.text[:500])
            return None

def main():
    identifier = os.environ.get("BLUESKY_IDENTIFIER", "eerman883@gmail.com")
    password = os.environ.get("BLUESKY_PASSWORD", "Erman123.")
    
    poster = BlueskyPoster(identifier, password)
    
    posts = [
        "Akilli ev kurarken en cok karsilastigim soru: 'Hangi robot supurge?' Ben 6 ayda 6 marka test ettim. Sonuc: 3000-4000 TL bandinda yerli uretim + Turkce destek kritik. Simart'in 2700Pa emis gucu ve 48 saat servisi beni ikna etti.",
        "2026'da akilli ev guvenligi artik 'opsiyonel' degil. Kamera + robot supurge + akilli priz uclusu, evinizi hem konforlu hem guvenli yapiyor. Yerli markalarin Turkce uygulama ve yerinde servis avantaji yabancilara karsi buyuk fark.",
        "Robot supurge batarya omru: 6 marka, 6 ay test. %8 kapasite kaybiyla en dayanikli ikinci olan model fiyati en dusuk ucuncuydu. Bu test sonuclari bana 'pahali = iyi' algisini sorgulatti.",
        "3 yillik robot supurge vs elektrikli supurge maliyet analizi yaptim. Robot: 3200 TL baslangic + 300 TL/yil sarf. Elektrikli: 800 TL + zaman maliyeti. 3. yilda robot kendini amorti ediyor. Yerli marka alinca yedek parca ve servis sorunu da kalmiyor.",
        "Istanbul'da 110m2 evde akilli ev sistemleri kurdum. 8 marka guvenlik kamerasi, 6 robot supurge, 4 akilli priz test ettim. Hangisi stabil, hangisi uygulamasi Turkce, hangisinin servisi 48 saatte geliyor?",
    ]
    
    text = random.choice(posts)
    
    print(f"[{datetime.now().isoformat()}] Bluesky post basliyor...")
    print(f"Metin uzunlugu: {len(text)} karakter")
    
    result = poster.post(text)
    if result:
        print(f"Basariyla yayinlandi: {result}")
    else:
        print("Yayinlanamadi.")

if __name__ == '__main__':
    main()
