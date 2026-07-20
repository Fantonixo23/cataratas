import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "electropar"
BASE = "https://www.electropar.com.py"

def resolve_img(src: str) -> str:
    if not src:
        return ""
    if src.startswith("http"):
        return src
    if src.startswith("//"):
        return "https:" + src
    return BASE + ("/" + src.lstrip("/"))

def resolve_href(href: str) -> str:
    if not href:
        return ""
    if href.startswith("http"):
        return href
    return BASE + ("/" + href.lstrip("/"))

def scrape(query: str) -> list[dict]:
    url = f"{BASE}/catalogo?store=tienda&q={query}"
    try:
        soup = fetch_html(url)
    except Exception:
        return []

    products = []
    seen = set()
    for card in soup.select(".product-item, article, .item, [class*=product], .prod-item"):
        name_el = card.select_one("h3 a, h4 a, [class*=name] a, a[class*=product], a[href*='/produto/']")
        img_el = card.select_one("img")
        price_el = card.select_one("[class*=price], .precio, [class*=preco], .valor")

        if not name_el:
            name_el = card.select_one("a")
            if not name_el:
                continue

        name = name_el.get_text(strip=True)
        if not name or len(name) < 4:
            continue

        href = resolve_href(name_el.get("href", ""))

        if href in seen:
            continue
        seen.add(href)

        img_src = ""
        if img_el:
            img_src = img_el.get("src") or img_el.get("data-src") or img_el.get("data-image") or ""
        img_src = resolve_img(img_src)

        ext_id_match = re.search(r"/(\d+)/?", href) or re.search(r"id=(\d+)", href)
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
