import sys, os
sys.stdout.reconfigure(encoding="utf-8")

# Try different HTTP approaches for blocked sites
# 1. Try requests library instead of curl_cffi
import requests as plain_requests

for url in [
    "https://nissei.com/py/celular",
    "https://www.mobilezone.com.py/",
    "https://madridcenterimportados.com/",
]:
    try:
        r = plain_requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=15)
        from bs4 import BeautifulSoup
        s = BeautifulSoup(r.text, "lxml")
        title = s.title.string[:50] if s.title else "NONE"
        print(f"OK {url.split('/')[2]}: {title}")
        # Count product links
        links = s.select('a[href*="/produto/"], a[href*="/producto/"], a[href*="/product/"]')
        print(f"  Product links: {len(links)}")
    except Exception as e:
        print(f"NO {url.split('/')[2]}: {e}")
