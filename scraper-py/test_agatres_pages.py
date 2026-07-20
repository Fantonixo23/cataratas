import sys
sys.stdout.reconfigure(encoding="utf-8")
from common import fetch_html

# Check if agatres has more pages after 82
for p in [83, 85, 90, 100, 120, 125, 127]:
    url = f"https://agatres.co/es/productos/page/{p}/"
    try:
        s = fetch_html(url, timeout=20)
        cards = s.select(".product, [class*=product]")
        real = 0
        for c in cards:
            if c.select_one("h2 a, h3 a, .product-title a"):
                real += 1
        print(f"Page {p}: {real} products")
    except Exception as e:
        print(f"Page {p}: ERROR {e}")
