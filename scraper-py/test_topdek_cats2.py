import sys
sys.stdout.reconfigure(encoding="utf-8")
from common import fetch_html

s = fetch_html("https://www.topdekinformatica.com.br/")
links = []
for a in s.select("a[href]"):
    h = a.get("href", "")
    txt = a.get_text(strip=True)
    if "/categoria/" in h and txt and txt not in links:
        links.append(txt)
        print(f"{txt}: {h}")

print(f"\nTotal categorias: {len(links)}")
