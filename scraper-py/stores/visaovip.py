import re
from common import fetch_html, parse_price

STORE_ID = "visaovip"

def scrape(query: str | None = None) -> list[dict]:
    soup = fetch_html("https://visaovip.com/es/")
    seen = set()

    products = []
    for a in soup.select("a[href*='/es/prod/']"):
        href = a.get("href", "")
        if not href or href in seen:
            continue
        seen.add(href)

        name = a.get_text(strip=True)
        if not name:
            continue
        name = re.sub(r"^(HOTOFERTA|OFERTAGAMER|OFERTA|HOT)\s*", "", name).strip()

        img = a.find("img")
        img_src = None
        if img:
            img_src = img.get("src") or img.get("data-src")

        full_url = f"https://visaovip.com{href}" if href.startswith("/") else href

        code_match = re.search(r"/(\d+)/?$", href)
        code = code_match.group(1) if code_match else ""

        price = None
        parent = a.find_parent()
        for p_cls in ["preco-promocional", "preco-de", "price", "valor", "preco"]:
            price_el = a.select_one(f".{p_cls}")
            if not price_el and parent:
                price_el = parent.select_one(f".{p_cls}")
            if price_el:
                price = parse_price(price_el.get_text(strip=True))
                break

        products.append({
            "name": name,
            "price": price,
            "image_url": img_src,
            "source_url": full_url,
            "external_id": code,
            "store_origin": STORE_ID,
        })

    return products
