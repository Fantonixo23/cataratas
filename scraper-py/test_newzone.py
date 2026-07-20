import sys
sys.stdout.reconfigure(encoding="utf-8")
from common import fetch_html

# Check newzone for more product pages
for url in [
    "https://newzone.com.py/",
    "https://newzone.com.py/categoria/celular",
    "https://newzone.com.py/categoria/informatica",
    "https://newzone.com.py/categoria/tv",
    "https://newzone.com.py/categoria/audio",
    "https://newzone.com.py/categoria/games",
    "https://newzone.com.py/categoria/hogar",
    "https://newzone.com.py/categoria/moda",
    "https://newzone.com.py/categoria/deportes",
    "https://newzone.com.py/categoria/juguetes",
    "https://newzone.com.py/categoria/belleza",
]:
    try:
        s = fetch_html(url, timeout=15)
        links = s.select('a[href*="/producto/"]')
        # Get unique hrefs
        unique_hrefs = set()
        for a in links:
            h = a.get("href", "")
            if h:
                unique_hrefs.add(h)
        print(f"{url.split('/')[-1] or 'home'}: {len(unique_hrefs)} product links")
    except Exception as e:
        print(f"{url.split('/')[-1] or 'home'}: ERROR {e}")
