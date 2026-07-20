import urllib.request, json
from bs4 import BeautifulSoup

BASE = "https://cellshop.com.py"

CATEGORIES = [
    ("Informatica", 415),
    ("Celulares", 694),
    ("Apple", 1015),
    ("Electronicos", 307),
    ("Accesorios_Tech", 13),
    ("Tablets", 682),
    ("Camaras", 1054),
    ("Electrodomesticos", 304),
    ("Automotivo", 94),
    ("Vigilancia", 1060),
]

for label, cat_id in CATEGORIES:
    for page in [1, 2]:
        url = f"{BASE}/todos-los-departamentos/tecnologia?cat={cat_id}&p={page}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            products = soup.select(".product-item")
            
            # Find pagination
            pages = set()
            for a in soup.select("a[href]"):
                href = a.get("href", "")
                if "?p=" in href:
                    t = a.get_text(strip=True)
                    if t.isdigit():
                        pages.add(int(t))
            
            if page == 1:
                print(f"{label} (cat={cat_id}): page1={len(products)} products, total_pages={sorted(pages)}")
            else:
                print(f"  page2={len(products)} products")
        except Exception as e:
            if page == 1:
                print(f"{label}: ERROR {e}")
