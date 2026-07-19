import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "electronica"

def scrape(query: str) -> list[dict]:
    url = f"https://www.electronica.com.py/buscar?q={query}"
    try:
        soup = fetch_html(url)
    except Exception:
        return []

    products = []
    for card in soup.select(".product-item, article, .item, [class*=product], tr.product, .produto-item"):
        name_el = card.select_one("h3 a, h4 a, .product-name a, [class*=nome] a, a[class*=product]")
        img_el = card.select_one("img")
        price_el = card.select_one("[class*=price], .precio, [class*=preco], .valor, .preco-promocional")

        if not name_el:
            name_el = card.select_one("a[href*='/produto/'], a[href*='/producto/'], a[href*='id_product=']")
            if not name_el:
                continue

        name = name_el.get_text(strip=True)
        if not name or len(name) < 4:
            continue

        href = name_el.get("href", "")
        if href and not href.startswith("http"):
            href = f"https://www.electronica.com.py{href}" if href.startswith("/") else f"https://www.electronica.com.py/{href}"

        img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
        if img_src and not img_src.startswith("http"):
            img_src = f"https:{img_src}" if img_src.startswith("//") else ""

        ext_id_match = re.search(r"id_product=(\d+)", href) or re.search(r"/prod/(\d+)", href) or re.search(r"/p/(\d+)", href)
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
