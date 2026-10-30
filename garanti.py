import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import asyncio
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

BASE_URL = "https://www.bonus.com.tr"
LIST_URL = f"{BASE_URL}/kampanyalar"

session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/156.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9"
})

# 1. Kampanya listesini indir
response = session.get(LIST_URL, timeout=30)
response.raise_for_status()
response.encoding = "utf-8"


soup = BeautifulSoup(response.text, "html.parser")


# 2. Kampanya detay bağlantılarını çıkar
# Bu örnekte tüm bağlantılar taranıyor.
# Gerçek projede kampanya kartlarına özgü seçici kullan.
urls = set()

for a in soup.select("a[href]"):
    href = a.get("href", "")
    full_url = urljoin(BASE_URL, href)

    if "/kampanyalar/" in full_url:
        urls.add(full_url)

print("Bulunan bağlantı sayısı:", len(urls))

# 3. Her kampanyanın detay sayfasını indir
for detail_url in sorted(urls):
    
    try:
        detail_response = session.get(detail_url, timeout=30)
        detail_response.raise_for_status()
        detail_response.encoding = "utf-8"
        detail_soup = BeautifulSoup(
            detail_response.text, "html.parser"
        )
        banka_adi = 'garanti'

       # 1. Sektör
        sector_1 = detail_soup.select_one(".campaign-detail__brand-sector a")
        sector=sector_1.get_text(strip=True) if sector_1 else None
        print("Sektör:", sector)
        
        # 2. Marka
        brand_section = detail_soup.select_one(".campaign-detail__brand-sector")
        brand_links = brand_section.find_all("a") if brand_section else []
        marka=  brand_links[1].get_text(strip=True) if len(brand_links) > 1 else None
        print("Marka:", marka)
        
        # 3. Katılmak için
        join_title = detail_soup.find("h2", string=lambda x: x and "KATILMAK İÇİN" in x)
        join_text = join_title.find_next("p") if join_title else None
        katilma_sartlari = join_text.get_text(" ", strip=True) if join_text else None
        print("Katılmak için:", katilma_sartlari)
        
        # 4. Nasıl kazanırım?
        how_title = detail_soup.find("h2", string=lambda x: x and "NASIL KAZANIRIM" in x)
        how_text = how_title.find_next("p") if how_title else None
        kampanya_detaylari= how_text.get_text(" ", strip=True) if how_text else None
        print("Nasıl kazanırım:", kampanya_detaylari)
        
        # 5. Diğer bilgileri (liste halinde)
        ul = detail_soup.select_one(
            'ul[aria-label="kampanyaya dahil kartlar ve diğer bilgiler"]'
        )
        
        other_info = []
        
        if ul:
            found_other_info = False
        
            for element in ul.find_all(["strong", "li"], recursive=False):
                if element.name == "strong":
                    if "Diğer Bilgiler" or "Kampanyaya Dahil Kartlar" in element.get_text(strip=True):
                        found_other_info = True
                elif element.name == "li" and found_other_info:
                    other_info.append(element.get_text(" ", strip=True))
                    
        
        
        diger_bilgiler = " - ".join(other_info)
        print("Diğer bilgiler:")
        print(diger_bilgiler)
        
        # 6. Kampanya başlangıç ve bitiş
        campaign_dates = detail_soup.select_one("p.campaign-date")
        
        kampanya_baslangic_bitis = campaign_dates.get_text(" ", strip=True) if campaign_dates else None
        print(
            "Kampanya başlangıç ve bitiş:",kampanya_baslangic_bitis
            
        )
        # 7. Bonus kullanım tarihleri
        bonus_dates_title = detail_soup.find(
            lambda tag: tag.name in ["h2", "h3", "h4"]
            and "BONUS GEÇERLİLİK TARİHİ" in tag.get_text(" ", strip=True).upper()
        )
        
        bonus_dates = bonus_dates_title.find_next("p") if bonus_dates_title else None
        
        puan_kullanim_tarihleri = bonus_dates.get_text(" ", strip=True) if bonus_dates else None
        print(
            "Bonus kullanım tarihleri:",
            puan_kullanim_tarihleri
        )
       
        title = (
            detail_soup.title.get_text(" ", strip=True)
            if detail_soup.title else None
        )
        baslik = title

        description = detail_soup.get_text(" ", strip=True)
          
        #print({
         #   "url": detail_url,
          #  "title": title,
           # "description": description
        #})
        
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
        katilma_sartlari, 
        kampanya_detaylari, 
        diger_bilgiler, 
        kampanya_baslangic_bitis, 
        puan_kullanim_tarihleri
        )
        
        cur.execute(sql, values)
        cnx.commit()
        

    except requests.RequestException as error:
        print("Hata:", detail_url, error)