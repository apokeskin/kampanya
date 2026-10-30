import json
import random
import time
from bs4 import BeautifulSoup
import mysql.connector
import requests

# MySQL Veritabanı Bağlantısı
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    port=3306,
    password="1982",
    database="kampanya",
    use_pure=True,
)
cur = cnx.cursor()

url = "https://www.maximum.com.tr/kampanyalar"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

all_urls = []

for script in soup.find_all("script", type="application/ld+json"):
  try:
    data = json.loads(script.get_text(strip=True))

    if data.get("@type") == "Organization":
      catalog = data.get("hasOfferCatalog", {})
      items = catalog.get("itemListElement", [])

      for entry in items:
        item = entry.get("item", {})
        campaign_url = item.get("url")

        if campaign_url:
          all_urls.append(campaign_url)

  except (json.JSONDecodeError, AttributeError):
    continue

# Tekrarlanan URL'leri kaldır
all_urls = list(dict.fromkeys(all_urls))

print("Toplam URL:", len(all_urls))
print(all_urls)



banka_adi = "is_bankasi"
sector = "to be done by AI"
marka = "to be done by AI"
puan_kullanim_tarihleri = "to be done by AI"

for campaign_url in all_urls:
  print(f"İşleniyor: {campaign_url}")

  try:
    response = requests.get(campaign_url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    html_content = soup.prettify()

    # Hammadde HTML'yi dosyaya kaydetme
    with open("soup_structure.txt", "w", encoding="utf-8") as file:
      file.write(html_content)

    # 1. Etiket ve Tarihler
    d_block_span = soup.select_one("span.d-block")
    kampanya_tarihleri_label = (
        d_block_span.get_text(strip=True) if d_block_span else "Bulunamadı"
    )

    text_dark_span = soup.select_one("span.text-dark")
    tarih_araligi = (
        text_dark_span.get_text(separator=" ", strip=True)
        if text_dark_span
        else "Bulunamadı"
    )

    # 2. Başlık
    campaign_title = soup.find(id=lambda x: x and "CampaignTitle" in x)
    kampanya_basligi = (
        campaign_title.get_text(strip=True) if campaign_title else "Bulunamadı"
    )

    # 3. Description İşlemleri
    campaign_desc = soup.find(id=lambda x: x and "CampaignDescription" in x)

    ilk_aciklama = "Bulunamadı"
    diger_kisimlar = []

    if campaign_desc:
      # A. Description içindeki ilk dolu 'div' etiketini doğrudan ilk açıklama olarak alıyoruz
      ilk_div = campaign_desc.find("div")
      if ilk_div:
        ilk_aciklama = ilk_div.get_text(separator=" ", strip=True)
        
      # B. Diğer blokları (<p>, <li>) topluyoruz (ilk açıklamadan farklı olanlar)
      bloklar = campaign_desc.find_all(["p", "li"])
      for b in bloklar:
        metin = b.get_text(separator=" ", strip=True)
        # İlk açıklamayla birebir aynı değilse ve daha eklenmediyse alalım
        if metin and metin != ilk_aciklama and metin not in diger_kisimlar:
          diger_kisimlar.append(metin)

      # C. Strong etiketlerinden sonra gelen düz metinleri de yakalayalım
      strong_etiketleri = campaign_desc.find_all("strong")
      for s in strong_etiketleri:
        strong_sonrasi = s.next_sibling
        if (
            strong_sonrasi
            and hasattr(strong_sonrasi, "string")
            and strong_sonrasi.string
        ):
          temiz_metin = strong_sonrasi.string.strip()

          if temiz_metin:
            baslik_ve_detay = f"{s.get_text(strip=True)} {temiz_metin}"

            if baslik_ve_detay not in diger_kisimlar:
              diger_kisimlar.append(baslik_ve_detay)

    # Diğer detaylar arasına " -- " koyarak birleştiriyoruz
    aciklama_metni = " -- ".join(diger_kisimlar)

    # Sonuçları ekrana yazdır
    print(f"Etiket: {kampanya_tarihleri_label}")
    print(f"Tarih Aralığı: {tarih_araligi}")
    print(f"Başlık: {kampanya_basligi}")
    print(f"İlk Açıklama: {ilk_aciklama}")
    print(f"Diğer Detaylar (Açıklamalar): {aciklama_metni}")

    # MySQL Kayıt İşlemleri
    sql = """
            INSERT INTO kampanya.main_table 
            (banka_adi, sector, marka, baslik, katilma_sartlari, kampanya_detaylari, diger_bilgiler, kampanya_baslangic_bitis, puan_kullanim_tarihleri) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    baslik = kampanya_basligi
    katilma_sartlari = ilk_aciklama
    kampanya_detaylari = aciklama_metni
    diger_bilgiler = ""
    kampanya_baslangic_bitis = tarih_araligi

    values = (
        banka_adi,
        sector,
        marka,
        baslik,
        katilma_sartlari,
        kampanya_detaylari,
        diger_bilgiler,
        kampanya_baslangic_bitis,
        puan_kullanim_tarihleri,
    )

    cur.execute(sql, values)
    cnx.commit()

    time.sleep(random.randint(5, 25))

  except requests.exceptions.RequestException as e:
    print(f"Bağlantı hatası ({campaign_url}): {e}")

# Bağlantıyı kapatma
cur.close()
cnx.close()