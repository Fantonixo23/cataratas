import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "cellshop"

def scrape(query: str) -> list[dict]:
    url = f"https://www.cellshop.com.py/catalogsearch/result/?q={query}"
    soup = fetch_html(url)

    products = []
    for card in soup.select(".product-item"):
        name_el = card.select_one(".product-item-link")
        price_el = card.select_one(".price")
        img_el = card.select_one("img")
        link_el = card.select_one("a.product-item-link")

        if not name_el or not link_el:
            continue

        href = link_el["href"]
        id_match = re.search(r"/id/(\d+)", href)
        if not id_match:
            id_match = re.search(r"/(\d+)-[^/]+/?$", href)
        external_id = id_match.group(1) if id_match else href.rstrip("/").split("/")[-1]
        products.append({
            "name": name_el.get_text(strip=True),
            "price": parse_price(price_el.get_text(strip=True) if price_el else None),
            "image_url": img_el["src"] if img_el and img_el.has_attr("src") else None,
            "source_url": href,
            "external_id": external_id,
            "store_origin": STORE_ID,
        })

    polite_delay()
    return products
