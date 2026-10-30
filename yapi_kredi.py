import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import random
import mysql.connector

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    port=3306,
    password="1982",
    database="kampanya", # Veritabanını burada belirtmek daha iyidir
    use_pure=True
)
cur = cnx.cursor()

url = "https://www.worldcard.com.tr/api/campaigns"

params = {
    "campaignSectorKey": "tum-kampanyalar",
    "campaignSectorId": "6d897e71-1849-43a3-a64f-62840e8c0442",
    "campaignTypeId": 0,
    "keyword": ""
}

headers = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
    "Content-Type": "application/json; charset=utf-8",
    "Referer": "https://www.worldcard.com.tr/kampanyalar",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/156.0.0.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest"
}

session = requests.Session()

# Tarayıcıdan aldığın güncel çerezleri gerekiyorsa ekle.
# session.cookies.update({...})

campaign_urls = []
page = 1

while True:
    headers["Page"] = str(page)

    try:
        response = session.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

    except (requests.RequestException, ValueError) as e:
        print(f"Sayfa {page} alınamadı. Hata: {e}")
        break

    items = data.get("Items", [])

    # Items boşsa döngüyü bitir
    if not items:
        print(f"Sayfa {page} boş döndü. İşlem tamamlandı.")
        break

    # Bu sayfadaki URL'leri listeye ekle
    for item in items:
        campaign_url = item.get("Url")

        if campaign_url:
            campaign_urls.append(campaign_url)

    print(
        f"Sayfa {page}: {len(items)} kampanya alındı. "
        f"Toplam URL: {len(campaign_urls)}"
    )

    page += 1

    # Sunucuya çok sık istek göndermemek için bekle
    time.sleep(2)

print("\nToplam URL sayısı:", len(campaign_urls))

# İlk 5 URL'yi kontrol et
print(campaign_urls[:5])





all_campaigns = []

base_url = "https://www.worldcard.com.tr"

banka_adi= "Yapı Kredi"
sector="genel"
marka ="genel"
for i, detail_url in enumerate(campaign_urls, start=1):

    # URL göreli ise tam URL'ye çevir
    detail_url = urljoin(base_url, detail_url)

   

    try:
        
        
        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
            "Content-Type": "application/json; charset=utf-8",
            "Referer": "https://www.worldcard.com.tr/kampanyalar",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/156.0.0.0 Safari/537.36"
            )
        }
        detail_response = session.get(detail_url,headers=headers, timeout=30)
        detail_response.raise_for_status()
        detail_response.encoding = "utf-8"

        soup = BeautifulSoup(
            detail_response.text, "html.parser"
        )

        result = {
            "url": detail_url
        }

        # 1. Sayfa title
        result["title"] = (
            soup.title.get_text(strip=True)
            if soup.title else None
        )

        # 2. Görsel alt ve src
        img = soup.find(
            "img",
            id="ContentPlaceHolder1_imgDetail"
        )

        result["alt"] = img.get("alt") if img else None
        result["src"] = (
            urljoin(base_url, img.get("src"))
            if img and img.get("src")
            else None
        )

        
        baslik= result["title"]
        

        # 3. Kampanya başlangıç-bitiş tarihi
        date_element = soup.select_one(
            ".campaign-list.start-end-date"
        )

        result["start_end_date"] = (
            date_element.get_text(" ", strip=True)
            if date_element else None
        )
        kampanya_baslangic_bitis = result["start_end_date"]
        

        # 4. Kampanya başvuru kanalları
        heading = soup.find(
            "h3",
            string=lambda s: (
                s and s.strip() == "Kampanya Başvuru Kanalları"
            )
        )

        if heading:
            section = heading.find_parent(
                "div",
                class_="campaign-list"
            )
            text_element = (
                section.select_one(".row p")
                if section else None
            )

            result["world_mobil"] = (
                text_element.get_text(" ", strip=True)
                if text_element else None
            )
        else:
            result["world_mobil"] = None

        

                # 5. Kampanya koşulları
        terms = soup.select_one(".campaign-terms")
        campaign_terms = {}
        
        if terms:
            elements = terms.find_all(["p", "ul"], recursive=False)
        
            current_heading = None
        
            for element in elements:
        
                if element.name == "p":
                    bold = element.find("b")
        
                    if bold:
                        current_heading = bold.get_text(" ", strip=True)
                        campaign_terms[current_heading] = []
        
                elif element.name == "ul" and current_heading:
                    li_texts = [
                        li.get_text(" ", strip=True)
                        for li in element.find_all("li", recursive=False)
                        if li.get_text(" ", strip=True)
                    ]
        
                    campaign_terms[current_heading].extend(li_texts)
        
        # Her başlığın li değerlerini " -- " ile birleştir
        for heading in campaign_terms:
            campaign_terms[heading] = " -- ".join(
                campaign_terms[heading]
            )
        
        
        
        katilma_sartlari = []
        kampanya_detaylari = []
        diger_bilgiler = []
        puan_kullanim_tarihleri=[]
        
        for heading, content in campaign_terms.items():
            if "katılım yapılma detayları" in heading.lower():
                katilma_sartlari.append(content)
            elif "dâhil" in heading.lower():
                kampanya_detaylari.append(content)
            elif "puan" in heading.lower():
                puan_kullanim_tarihleri.append(content)
            else :
                diger_bilgiler.append(content)
                
        
        
       
        
        # Kampanyanın tüm verilerini sakla
        all_campaigns.append(result)
        
        sql = """
            INSERT INTO kampanya.main_table 
            (banka_adi, sector, marka, baslik, katilma_sartlari, kampanya_detaylari, diger_bilgiler, kampanya_baslangic_bitis, puan_kullanim_tarihleri) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
        banka_adi, 
        sector, 
        marka, 
        baslik, 
        ", ".join(katilma_sartlari),
        ", ".join(kampanya_detaylari),
        ", ".join(diger_bilgiler),
        kampanya_baslangic_bitis, 
        ", ".join(puan_kullanim_tarihleri)
        )
        
        cur.execute(sql, values)
        cnx.commit()
        
        
        
    except requests.RequestException as e:
        print("Kampanya alınamadı:", e)

        # Hata alan URL'yi de kaybetmemek için kaydet
        all_campaigns.append({
            "url": detail_url,
            "error": str(e)
        })
        
    # Siteye peş peşe çok sık istek göndermemek için
    time.sleep(random.randint(5, 25))

print("\nİşlem tamamlandı.")
print("İşlenen kampanya sayısı:", len(all_campaigns))


