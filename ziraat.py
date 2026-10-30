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

url = "https://www.bankkart.com.tr/api/Campaigns/GetMoreShow"

headers = {
    "Accept": "*/*",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.bankkart.com.tr/kampanyalar",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

params = {
    "indexNo": 1,
    "CategoryId": "",
    "cuzdan": "",
    "arsiv": "",
    "type": "Bireysel"
}


seen_urls = set()

campaign_urls = []

with requests.Session() as session:
    session.headers.update(headers)

    while True:
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        if isinstance(data, dict):
            campaigns = data.get("Items", [])
        elif isinstance(data, list):
            campaigns = data
        else:
            campaigns = []

        if not campaigns:
            print(f"{params['indexNo']}. indekste kampanya bulunamadı. İşlem tamamlandı.")
            break

        new_count = 0

        for campaign in campaigns:
            category_seo = campaign.get("Category", {}).get("SeoName")
            campaign_seo = campaign.get("SeoName")

            if category_seo and campaign_seo:
                campaign_url = (
                    "https://www.bankkart.com.tr/kampanyalar/"
                    + category_seo + "/" + campaign_seo
                )
                if campaign_url not in seen_urls:
                    campaign_urls.append(campaign_url)
                    seen_urls.add(campaign_url)
                    new_count += 1
                    

        

        # Yeni kampanya gelmiyorsa sonsuz döngüyü önle
        if new_count == 0:
            break
        
        params["indexNo"] += 1
        
        time.sleep(random.randint(1, 7))


        
print(*campaign_urls, sep="\n")
print(len(campaign_urls))


banka_adi="Ziraat"
marka= "to be done by AI"
kampanya_detaylari= "to be done by AI"
puan_kullanim_tarihleri="to be done by AI"



for campaing_url in campaign_urls :
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36",
        "Referer": "https://www.bankkart.com.tr/kampanyalar"
    }
    
    response = requests.get(campaing_url, headers=headers, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Kampanya adı
    title_tag = soup.find("h1")
    campaign_title = title_tag.get_text(" ", strip=True) if title_tag else None
    
    # Meta description
    meta_description = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_description.get("content") if meta_description else None
    
    # Kampanya dönemi
    # Kampanya dönemi
    period_tag = soup.find("p", class_="campdate")
    campaign_period = period_tag.get_text(" ", strip=True) if period_tag else None
    
    # Kampanya dönemi etiketi
    period_label_tag = soup.find("p", class_="camptext")
    period_label = period_label_tag.get_text(" ", strip=True) if period_label_tag else None
    
    # Son gün
    last_date_tag = soup.find("span", class_="last-date")
    last_date = last_date_tag.get_text(" ", strip=True) if last_date_tag else None
    
    print("KAMPANYA DÖNEMİ:", campaign_period)
    print("DÖNEM ETİKETİ:", period_label)
    print("SON GÜN:", last_date)
    
    
    #sector
    sector = None
    
    for p in soup.find_all("p"):
        strong = p.find("strong")
    
        if strong and "Sektör" in strong.get_text(strip=True):
            sector = p.get_text(" ", strip=True)
            sector = sector.replace("Sektör:", "").strip()
            break
    
    print("SEKTÖR:", sector)
    
            # Kampanya Koşulları
        
    
    campaign_conditions = None
    
    detail_content = soup.select_one("div.detail-content")
    
    if detail_content:
    
        # İstenmeyen bölümleri çıkar
        exclude_selectors = [
            "div.col-xs-12.col-md-6.pull-right.pr0",
            "script",
            "style",
            "form"
        ]
    
        for selector in exclude_selectors:
            for element in detail_content.select(selector):
                element.decompose()
    
        # HTML içeriğini metne dönüştür
        lines = []
    
        for element in detail_content.find_all(["p", "li"]):
    
            # İç içe li elemanlarını ayrı ayrı al
            if element.name == "li":
                if element.find_parent("li"):
                    continue
    
                text = element.get_text(" ", strip=True)
    
                if text:
                    lines.append("- " + text)
    
            elif element.name == "p":
                if not element.find_parent("li"):
                    text = element.get_text(" ", strip=True)
    
                    if text:
                        lines.append(text)
    
        campaign_conditions = "\n".join(lines)


    
    
    # Sonuçları yazdır
    print("KAMPANYA ADI:", campaign_title)
    print("META DESCRIPTION:", meta_description)
    print("KAMPANYA DÖNEMİ:", campaign_period)
    print("SEKTÖR:", sector)
    

    
    print("KAMPANYA KOŞULLARI:")
    print(campaign_conditions)
    
    
    sql = """
            INSERT INTO kampanya.main_table 
            (banka_adi, sector, marka, baslik, katilma_sartlari, kampanya_detaylari, diger_bilgiler, kampanya_baslangic_bitis, puan_kullanim_tarihleri) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    baslik=meta_description
    katilma_sartlari=campaign_conditions
    diger_bilgiler=""
    kampanya_baslangic_bitis=campaign_period
    
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

    time.sleep(random.randint(5, 50))
    
    
# Bağlantıyı kapatma
cur.close()
cnx.close()
    