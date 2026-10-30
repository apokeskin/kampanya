import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
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



url = "https://www.qnbcard.com.tr/api/Campaigns"
base_url = "https://www.qnbcard.com.tr/kampanyalar/"

params = {
    "isArchived": "false",
    "sectorId": "",
    "brandId": "",
    "categoryId": "",
    "keyword": "",
    "year": "",
    "month": ""
}

session = requests.Session()
session.headers.update({
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Bone-Language": "TR",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.qnbcard.com.tr/kampanyalar",
    "User-Agent": "Mozilla/5.0"
})
all_campaigns = []
page = 1

banka_adi="QNB"
sector="to be done by AI"
marka="to be done by AI"
diger_bilgiler=""
kampanya_baslangic_bitis="to be done by AI OR with include"
puan_kullanim_tarihleri= "to be done by AI OR with include"
while True:
    session.headers["Page"] = str(page)

    response = session.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    items = data.get("Items", [])

    if not items:
        break

    for item in items:
        title = item.get("Title")
        content_html = item.get("Content", "")

        content_soup = BeautifulSoup(content_html, "html.parser")

        # Paragraflar
        content = " ".join(
            p.get_text(" ", strip=True)
            for p in content_soup.find_all("p")
        )

        # Li elementleri
        li_list = "--".join(
            li.get_text(" ", strip=True)
            for li in content_soup.find_all("li")
            if li.get_text(" ", strip=True)
        )

        result = {
            "title": title,
            "content": content,
            "li_list": li_list
        }
        baslik=title
        kampanya_detaylari=content
        katilma_sartlari=li_list
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
        katilma_sartlari,
        kampanya_detaylari,
        diger_bilgiler,
        kampanya_baslangic_bitis, 
        puan_kullanim_tarihleri
        )
        
        cur.execute(sql, values)
        cnx.commit()
        
        
        
    
    
    print(f"Page {page}: {len(items)} kampanya")
    
    page += 1

print("\nİşlem tamamlandı.")
print("Toplam kampanya:", len(all_campaigns))