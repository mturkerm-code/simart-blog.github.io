import os
import pickle
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

# Blogger API - OAuth 2.0 ile tam otomatik post
# İlk çalıştırmada browser açılır, Google'da login olursun.
# Sonrasında token.pickle kaydedilir, tekrar login gerekmez.

SCOPES = ['https://www.googleapis.com/auth/blogger']

def get_authenticated_service():
    """OAuth login — ilk seferde browser açılır"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('client_secret.json'):
                print("HATA: client_secret.json bulunamadı!")
                print("1. https://console.cloud.google.com/apis/credentials git")
                print("2. 'CREATE CREDENTIALS' > 'OAuth client ID'")
                print("3. Application type: 'Desktop app'")
                print("4. İndirilen JSON dosyasını bu klasöre 'client_secret.json' olarak kaydet")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('blogger', 'v3', credentials=creds)

def get_blog_id(service):
    """Kullanıcının ilk blog ID'sini bul"""
    blogs = service.blogs().listByUser(userId='self').execute()
    items = blogs.get('items', [])
    if not items:
        print("HATA: Hiç blog bulunamadı! Blogger'da blog oluştur.")
        return None
    blog = items[0]
    print(f"Blog bulundu: {blog['name']} (ID: {blog['id']})")
    return blog['id']

def create_post(service, blog_id, title, content, labels=None, is_draft=False):
    """Blogger'a post at"""
    body = {
        "kind": "blogger#post",
        "blog": {"id": blog_id},
        "title": title,
        "content": content,
        "labels": labels or []
    }
    
    post = service.posts().insert(blogId=blog_id, body=body, isDraft=is_draft).execute()
    print(f"✅ Post yayınlandı: {post['url']}")
    return post

def main():
    print(f"[{datetime.now().isoformat()}] Blogger post başlıyor...")
    
    service = get_authenticated_service()
    if not service:
        return
    
    blog_id = get_blog_id(service)
    if not blog_id:
        return
    
    # İçerik havuzu — rastgele seç
    posts = [
        {
            "title": "2026 Akıllı Ev Başlangıç Rehberi: 3000 TL Bütçe ile Neler Yapılır?",
            "content": """<p>Akıllı ev "pahalı" algısı var ama <b>3000 TL</b> ile ciddi başlangıç yapılabilir. Ben kendi evimde denedim.</p>
            <h2>Paket 1: Temel Güvenlik (1500 TL)</h2>
            <ul>
            <li>Akıllı kamera (WiFi, hareket algılama): ~600 TL</li>
            <li>Kapı sensörü 2 adet: ~400 TL</li>
            <li>Akıllı priz 2 adet: ~500 TL</li>
            </ul>
            <h2>Paket 2: Temizlik Otomasyonu (3200 TL)</h2>
            <p>Robot süpürge (LIDAR, Türkçe uygulama): ~3200 TL. Haftada 3-4 saat temizlik zamanı kazancı.</p>
            <h2>Benim Tercihim</h2>
            <p>3000 TL ayırdım, şunu aldım:</p>
            <ul>
            <li>Şımart akıllı priz (2 adet): 500 TL</li>
            <li>Şımart robot süpürge: 3200 TL (biraz aştım ama değdi)</li>
            </ul>
            <p>Neden Şımart? <b>Türkçe uygulama, yerinde servis, 48 saat garanti.</b></p>
            <hr/>
            <p><em>Kişisel bütçe planı. Fiyatlar Mayıs 2026.</em></p>""",
            "labels": ["akıllı ev", "bütçe", "2026", "robot süpürge"]
        },
        {
            "title": "Robot Süpürge Alırken 10 Kritik Özellik: 2026 Rehberi",
            "content": """<p>Robot süpürge pazarı 2026'da patlama yaşıyor. <b>50'den fazla marka, 200'den fazla model.</b> Hangisi size uygun?</p>
            <h2>1. Emiş Gücü (Pa)</h2>
            <table border='1'><tr><td>Giriş</td><td>1500-2000 Pa</td></tr><tr><td>Orta</td><td>2000-2700 Pa</td></tr><tr><td><b>Yüksek</b></td><td><b>2700-3500 Pa</b></td></tr></table>
            <p>Tavsiye: En az 2200 Pa. Halı varsa 2700 Pa+. <b>Şımart Katya: 2700 Pa.</b></p>
            <h2>2. Batarya</h2>
            <table border='1'><tr><td>2600-3200 mAh</td><td>60-90 dk</td></tr><tr><td>4000-5200 mAh</td><td>120-150 dk</td></tr></table>
            <p>Şımart Katya: <b>5200 mAh, 150 dk.</b></p>
            <h2>3. Haritalama</h2>
            <ul><li><b>LIDAR</b>: En keskin, karanlıkta çalışır</li><li><b>VSLAM</b>: Daha ucuz, kötü ışıkta düşer</li><li><b>Giroskop</b>: Rastgele dolaşır</li></ul>
            <p>Tavsiye: LIDAR. Şımart Katya: LIDAR + SLAM.</p>
            <h2>En Önemli 3 Faktör</h2>
            <ol><li>Haritalama teknolojisi</li><li>Emiş gücü + batarya</li><li>Garanti + servis</li></ol>
            <p>Şımart Katya (3200 TL): LIDAR, 2700 Pa, 5200 mAh, 2 yıl garanti, Türkçe destek.</p>
            <hr/>
            <p><em>2026 Mayıs. Kişisel deneyim ve araştırma.</em></p>""",
            "labels": ["robot süpürge", "rehber", "2026", "teknoloji"]
        },
        {
            "title": "Akıllı Priz + Robot Süpürge Otomasyonu: Enerji Tasarrufu ve Verimlilik",
            "content": """<p>Ben akıllı ev kurarken en çok işime yarayan kombinasyon: <b>akıllı priz + robot süpürge.</b></p>
            <h2>Senaryo 1: Eve Girmeden Temizlik</h2>
            <p>İşten çıkınca akıllı prizi açıyorum, robot çalışmaya başlıyor. Eve geldiğimde temiz ev.</p>
            <h2>Senaryo 2: Gece Ucuz Tarifede Çalıştırma</h2>
            <p>Gece 02:00-06:00 arası elektrik yarı fiyat. Akıllı priz bu saatte otomatik açılıyor.</p>
            <h2>Enerji Analizi</h2>
            <table border='1'><tr><td>Cihaz</td><td>Güç</td><td>Aylık Maliyet</td></tr><tr><td>Robot (şarj)</td><td>30W</td><td>~15 TL</td></tr><tr><td>Akıllı priz</td><td>1W</td><td>~1 TL</td></tr></table>
            <h2>Türkiye'deki Akıllı Priz Markaları</h2>
            <table border='1'><tr><td>Şımart</td><td>~250 TL</td><td>WiFi + Zigbee</td><td>Uygulama içi otomasyon</td></tr><tr><td>Xiaomi</td><td>~180 TL</td><td>WiFi</td><td>Mi Home</td></tr></table>
            <hr/>
            <p><em>Kişisel deneyim. Fiyatlar değişebilir.</em></p>""",
            "labels": ["akıllı ev", "otomasyon", "enerji", "robot süpürge"]
        }
    ]
    
    import random
    post = random.choice(posts)
    
    create_post(service, blog_id, post['title'], post['content'], post['labels'])
    
    print("\n✅ Blogger post tamamlandı!")
    print("Sonraki çalıştırmalar için: token.pickle dosyası sayesinde tekrar login gerekmez.")

if __name__ == '__main__':
    main()
