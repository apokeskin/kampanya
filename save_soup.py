import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import random
import mysql.connector

url ="https://www.bankkart.com.tr/kampanyalar/diger-kampanyalar/yurt-disi-online-alisverislerinize-5500-tl-jest-lira"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Make the HTML look structured and pretty
pretty_html = soup.prettify()

# Save to a text file
with open("bankkart.txt", "w", encoding="utf-8") as file:
    file.write(pretty_html)