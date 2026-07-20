import sys
sys.stdout.reconfigure(encoding="utf-8")
from common import fetch_html

s = fetch_html("https://www.topdekinformatica.com.br/")
# Find product links on homepage
for a in s.select('a[href*="/produto/"]'):
    h = a.get("href", "")
    txt = a.get_text(strip=True)
    img = a.select_one("img")
    alt = img.get("alt", "") if img else ""
    print(f"{txt or alt[:40]}: {h[:80]}")
