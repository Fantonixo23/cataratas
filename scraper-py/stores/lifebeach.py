import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "lifebeach"

CATEGORIES = ["beach-tennis", "roupas", "acessorios", "padel", "tenis"]

def scrape(query: str) -> list[dict]:
    products = []
    for cat in CATEGORIES:
        url = f"https://www.lifebeach.com.py/categoria/{cat}"
        try:
            soup = fetch_html(url)
        except Exception:
            continue

        for card in soup.select(".product, .product-wrap, [class*=product]"):
            name_el = card.select_one(".product-name, [class*=name], h2, h3, h4")
            price_el = card.select_one(".product-price, .price, .preco, [class*=price]")
            img_el = card.select_one("img")
            link_el = card.select_one("a[href*='/produto/']") or card.select_one("a[href*='/producto/']") or card.select_one(".product-name a") or card.select_one("a")

            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 3:
                continue

            href = link_el.get("href", "") if link_el else ""
            if href and not href.startswith("http"):
                href = "https://www.lifebeach.com.py" + (href if href.startswith("/") else "/" + href)

            img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
            if img_src and not img_src.startswith("http"):
                img_src = "https:" + img_src if img_src.startswith("//") else ""

            ext_id_match = re.search(r"/(\\d+)/?", href) or re.search(r"id=(\\d+)", href)
            external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

            products.append({
                "name": name,
                "price": parse_price(price_el.get_text(strip=True) if price_el else None),
                "image_url": img_src or None,
                "source_url": href,
                "external_id": external_id,
                "store_origin": STORE_ID,
            })

        polite_delay()
    return products
