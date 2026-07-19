import sys
sys.stdout.reconfigure(encoding='utf-8')

from common import fetch_html

soup = fetch_html("https://www.cellshop.com.py/catalogsearch/result/?q=iphone")

productos = soup.select(".product-item")
print(f"Total productos encontrados: {len(productos)}")

for i, card in enumerate(productos[:3]):
    print(f"\n--- Producto {i+1} ---")
    name_el = card.select_one(".product-item-link")
    price_el = card.select_one(".price")
    img_el = card.select_one("img")
    link_el = card.select_one("a.product-item-link")

    print(f"  Nombre: {name_el.get_text(strip=True) if name_el else 'N/A'}")
    print(f"  Precio (text): {price_el.get_text(strip=True) if price_el else 'N/A'}")
    print(f"  Imagen src: {img_el.get('src') if img_el and img_el.has_attr('src') else 'N/A'}")
    
    if link_el and link_el.has_attr('href'):
        href = link_el['href']
        print(f"  Link: {href}")
        external_id = href.rstrip('/').split("/")[-1]
        print(f"  External ID: {external_id}")
    else:
        print(f"  Link: N/A")
    
    if price_el:
        price_text = price_el.get_text(strip=True)
        import re
        digits = re.sub(r"[^\d]", "", price_text)
        print(f"  Price parsed: {float(digits) if digits else None}")
