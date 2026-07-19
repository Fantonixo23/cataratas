import sys
sys.stdout.reconfigure(encoding='utf-8')

from common import fetch_html

soup = fetch_html("https://visaovip.com/es/")
links = soup.select("a[href*='/es/prod/']")

for a in links[:3]:
    href = a.get("href")
    name = a.get("title") or ""
    print(f"href: {href}")
    print(f"title attr: '{a.get('title')}'")
    print(f"text: '{a.get_text(strip=True)[:80]}'")
    print(f"img src: {a.find('img') and (a.find('img').get('src') or a.find('img').get('data-src'))}")
    
    # Find price
    parent = a.find_parent()
    for cls in ["preco-promocional", "preco-de", "price", "valor", "preco"]:
        price_el = a.select_one(f".{cls}")
        if not price_el and parent:
            price_el = parent.select_one(f".{cls}")
        if price_el:
            print(f"  price ({cls}): {price_el.get_text(strip=True)}")
            break
    print()
