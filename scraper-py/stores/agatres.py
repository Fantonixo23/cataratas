import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "agatres"

def scrape(query: str = "") -> list[dict]:
    all_products = []

    page = 1
    max_pages = 130  # all pages (last page is ~127)
    empty_pages = 0

    while page <= max_pages:
        url = f"https://agatres.co/es/productos/page/{page}/" if page > 1 else "https://agatres.co/es/productos/"
        try:
            soup = fetch_html(url, timeout=30)
        except Exception:
            break

        found = 0
        for card in soup.select(".product, [class*=product]"):
            # Skip category cards (no price, short names)
            name_el = card.select_one("h2 a, h3 a, .product-title a, .woocommerce-loop-product__title, .wd-entities-title a")
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 5:
                continue

            price_el = card.select_one(".price, .amount, .preco, .woocommerce-Price-amount")
            img_el = card.select_one("img")
            link_el = name_el if name_el.name == "a" else card.select_one("a[href*='/es/producto/']")

            if not link_el:
                continue
            href = link_el.get("href", "")
            if not href.startswith("http"):
                href = "https://agatres.co" + href

            img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
            if img_src and not img_src.startswith("http"):
                img_src = "https:" + img_src if img_src.startswith("//") else ""

            ext_id_match = re.search(r"/producto/([^/]+)", href) or re.search(r"/(\d+)/?", href) or re.search(r"p=(\d+)", href)
            external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

            all_products.append({
                "name": name,
                "price": parse_price(price_el.get_text(strip=True) if price_el else None),
                "image_url": img_src or None,
                "source_url": href,
                "external_id": external_id,
                "store_origin": STORE_ID,
            })
            found += 1

        print(f"  agatres page {page}: {found} productos")
        if found == 0:
            empty_pages += 1
            if empty_pages >= 2:
                break
        else:
            empty_pages = 0

        page += 1
        polite_delay(0.5, 1.5)

    return all_products
