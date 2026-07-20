import sys
sys.stdout.reconfigure(encoding="utf-8")
from common import fetch_html

# Check elegancia for more category pages
s = fetch_html("https://www.eleganciacompany.com/")
for a in s.select('a[href*="menu_id="]'):
    h = a.get("href", "")
    t = a.get_text(strip=True)
    if t and len(t) > 2:
        print(f"  {t}: {h}")

# Check all product links count
import re
all_links = set()
for a in s.select('a[href*="/productos/"]'):
    h = a.get("href", "")
    if h and h not in all_links:
        all_links.add(h)

print(f"\nTotal product links on homepage: {len(all_links)}")

# Try the all products page
try:
    s2 = fetch_html("https://www.eleganciacompany.com/productos")
    links2 = set()
    for a in s2.select('a[href*="/productos/"]'):
        if a.get("href","") and not a.get("href","").startswith("?"):
            links2.add(a.get("href",""))
    print(f"Products at /productos: {len(links2)}")
except Exception as e:
    print(f"Error /productos: {e}")
