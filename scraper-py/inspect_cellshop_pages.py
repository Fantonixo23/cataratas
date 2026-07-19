import sys, re
sys.stdout.reconfigure(encoding='utf-8')

from common import fetch_html

soup = fetch_html("https://www.cellshop.com.py/catalogsearch/result/?q=iphone")

# Check for pagination
pagination = soup.select(".pages a, .pagination a, .pager a, a[aria-label*='Page'], .page a, .pages-item-next a, li.page a")
if pagination:
    print(f"Paginación encontrada: {len(pagination)} links")
    for a in pagination[:5]:
        print(f"  {a.get('href')} → {a.get_text(strip=True)}")
else:
    print("No se encontró paginación")

# Check for "next" link
next_link = soup.select_one("a.next, a[rel='next'], .next i, .pages-item-next a")
if next_link:
    print(f"Next: {next_link.get('href')}")
else:
    print("No hay link 'next'")

# Find all product links and check if they have distinct URLs
product_links = soup.select("a.product-item-link")
urls = set()
for a in product_links:
    href = a.get("href")
    if href:
        # Extract product ID/code from URL
        parts = href.rstrip("/").split("/")
        code = parts[-1] if parts else href
        url_code = code.split("-")[0] if "-" in code else code
        urls.add(url_code)

print(f"\n{len(urls)} URLs únicas de productos")
print(f"Primeras: {list(urls)[:5]}")

# Try category pages
cats = ["celulares", "tecnologia", "electronica", "hogar"]
for cat in cats:
    try:
        soup2 = fetch_html(f"https://www.cellshop.com.py/{cat}")
        items = soup2.select(".product-item")
        if items:
            first = items[0].select_one(".product-item-link")
            print(f"\n/{cat}: {len(items)} prod, primero: {first.get_text(strip=True)[:40] if first else 'N/A'}")
    except Exception as e:
        print(f"\n/{cat}: ERROR: {e}")
