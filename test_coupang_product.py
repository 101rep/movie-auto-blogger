import requests
from bs4 import BeautifulSoup
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.coupang.com/vp/products/7640113464?itemId=20297548731"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}

try:
    r = requests.get(url, headers=headers, timeout=10)
    print("Status code:", r.status_code)
    soup = BeautifulSoup(r.text, 'html.parser')
    title = soup.find("title")
    print("Page Title:", title.string if title else "No title")
    og_title = soup.find("meta", property="og:title")
    print("OG Title:", og_title["content"] if og_title else "No og:title")
    og_img = soup.find("meta", property="og:image")
    print("OG Image:", og_img["content"] if og_img else "No og:image")
    og_desc = soup.find("meta", property="og:description")
    print("OG Desc:", og_desc["content"] if og_desc else "No og:description")
except Exception as e:
    print("Error:", e)
