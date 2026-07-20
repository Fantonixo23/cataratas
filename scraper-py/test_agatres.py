import sys
sys.stdout.reconfigure(encoding="utf-8")
from common import fetch_html

# Test agatres selectors
s = fetch_html("https://agatres.co/es/productos/", 30)
print(f"Page title: {s.title.string if s.title else 'NONE'}")

# Find correct product card selector
cards = s.select(".product, [class*=product]")
print(f"Total [class*=product]: {len(cards)}")

real = 0
for c in cards:
    title = c.select_one("h2 a, h3 a, .product-title a, .woocommerce-loop-product__title, .wd-entities-title a")
    if not title:
        title = c.select_one("a[href*='agatres']")
    if title:
        real += 1
        if real <= 3:
            name = title.get_text(strip=True)
            price = c.select_one(".price, .amount, .preco, .woocommerce-Price-amount")
            img = c.select_one("img")
            link = title if title.name == "a" else title.find_parent("a") or title.select_one("a")
            href = link.get("href", "") if link else ""
            print(f"  NAME: {name[:50]}")
            print(f"  PRICE: {price.get_text(strip=True)[:30] if price else 'NONE'}")
            print(f"  LINK: {href[:60]}")
            print(f"  IMG: {img.get('src','')[:60] if img else 'NONE'}")
            print(f"  ---")

print(f"Real products: {real}")

# Pagination
pages = s.select(".page-numbers a, .pagination a, a.page-link")
print(f"Pagination links: {len(pages)}")
for p in pages:
    txt = p.get_text(strip=True)
    href = p.get("href", "")
    print(f"  '{txt}' -> {href[:60]}")
