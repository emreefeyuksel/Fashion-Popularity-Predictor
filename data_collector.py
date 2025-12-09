import os
import requests
from bs4 import BeautifulSoup
import time


def download_images(url, save_folder, max_images=50):
    """
    Verilen URL'den resimleri akıllıca bulur ve indirir.
    Birden fazla CSS seçiciyi (selector) sırasıyla dener.
    """
    # 1. Klasör yoksa oluştur
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        print(f"📁 Klasör oluşturuldu: {save_folder}")

    # 2. Bot gibi görünmemek için User-Agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"🌐 Bağlanılıyor: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'lxml')

        # --- AKILLI SEÇİCİ KISMI ---
        # LCW'nin olası resim sınıflarını sırasıyla deniyoruz
        possible_selectors = [
            "img.product-image",  # En yaygın olan
            "img.product-item__image",  # Yeni tasarım ihtimali
            ".product-card img",  # Genel kapsayıcı
            "img.lazy"  # Bazen lazy load kullanılır
        ]

        img_tags = []
        used_selector = ""

        for selector in possible_selectors:
            found_tags = soup.select(selector)
            if len(found_tags) > 0:
                img_tags = found_tags
                used_selector = selector
                print(f"✅ '{selector}' ile {len(img_tags)} adet resim yakalandı.")
                break

        if len(img_tags) == 0:
            print("⚠️ HİÇ RESİM BULUNAMADI! Site yapısı farklı olabilir.")
            print("İpucu: Sayfayı tarayıcıda açıp F12 ile resim kodunu kontrol et.")
            return

        # --- İNDİRME DÖNGÜSÜ ---
        count = 0
        for i, img in enumerate(img_tags):
            if count >= max_images:
                break

            # Resim linkini yakala (farklı etiket ihtimalleri)
            img_url = img.get('data-src') or img.get('src') or img.get('data-original')

            # Link düzeltme (örn: //image.jpg -> https://image.jpg)
            if img_url and img_url.startswith("//"):
                img_url = "https:" + img_url

            # Sadece geçerli resim linklerini al
            if img_url and "http" in img_url and (".jpg" in img_url or ".jpeg" in img_url or ".webp" in img_url):
                try:
                    img_data = requests.get(img_url, headers=headers, timeout=5).content

                    # Dosya isimlendirme
                    prefix = os.path.basename(save_folder)
                    filename = os.path.join(save_folder, f"{prefix}_{count}.jpg")

                    with open(filename, 'wb') as handler:
                        handler.write(img_data)

                    # Konsolu çok doldurmamak için her 10 resimde bir bilgi verelim
                    if count % 10 == 0:
                        print(f"   ⬇️ {count + 1}. resim indirildi...")

                    count += 1
                    time.sleep(0.1)

                except Exception as e:
                    pass  # Hatalı resmi atla, devam et

        print(f"🏁 TAMAMLANDI! {save_folder} klasörüne toplam {count} resim indi.\n")

    except Exception as e:
        print(f"⛔ Kritik Hata: {e}")


# --- AYARLAR VE ÇALIŞTIRMA ---

if __name__ == "__main__":
    # SENİN VERDİĞİN LİNKLER

    # 1. Popüler (Çok Satanlar)
    popular_link = "https://www.lcw.com/mvc/populer-erkek-urunleri?urun-tipi=tisort"

    # 2. Popüler Olmayan (İndirim Oranı Yüksek / Stok Eritme)
    unpopular_link = "https://www.lcw.com/erkek-tisort-t-345?siralama=indirim-orani"

    print("--- SCRAPING BAŞLIYOR ---\n")

    # Popüler verileri indir
    download_images(popular_link, "dataset/popular", max_images=100)

    # Normal verileri indir
    download_images(unpopular_link, "dataset/unpopular", max_images=100)