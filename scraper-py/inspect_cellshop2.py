import sys
sys.stdout.reconfigure(encoding='utf-8')

from common import fetch_html

urls = [
    ("?q=iphone", "https://www.cellshop.com.py/catalogsearch/result/?q=iphone"),
    ("?q=samsung", "https://www.cellshop.com.py/catalogsearch/result/?q=samsung"),
    ("?q=xxxxxx", "https://www.cellshop.com.py/catalogsearch/result/?q=xxxxxx"),
    ("categoria/celulares", "https://www.cellshop.com.py/celulares"),
    ("categoria/notebook", "https://www.cellshop.com.py/notebook"),
]

for label, url in urls:
    try:
        soup = fetch_html(url, timeout=10)
        title = soup.title.string if soup.title else "N/A"
        items = soup.select(".product-item")
        first_name = items[0].select_one(".product-item-link").get_text(strip=True)[:60] if items else "N/A"
        price = items[0].select_one(".price").get_text(strip=True) if items and items[0].select_one(".price") else "N/A"
        print(f"{label:30s} → {len(items):2d} prod | {first_name} | {price}")
    except Exception as e:
        print(f"{label:30s} → ERROR: {e}")
