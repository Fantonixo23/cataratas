import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "mobilezone"

def scrape(query: str) -> list[dict]:
    for url in [
        f"https://www.mobilezone.com.py/busca?q={query}",
        f"https://www.mobilezone.com.py/",
    ]:
        try:
            soup = fetch_html(url)
            if soup.title and soup.title.string and "Mobile" in soup.title.string:
                break
        except Exception:
            continue
    else:
        return []

    products = []
    for card in soup.select("[class*=product], [class*=item], .card, article, [class*=produto], .grid-item, li[class]"):
        name_el = card.select_one("h2 a, h3 a, h4 a, [class*=name] a, [class*=title] a, a[href*='/produto/'], a[href*='/product/']")
        img_el = card.select_one("img")
        price_el = card.select_one("[class*=price], .precio, [class*=preco], .valor")

        if not name_el:
            continue

        name = name_el.get_text(strip=True)
        if not name or len(name) < 4:
            continue

        href = name_el.get("href", "")
        if href and not href.startswith("http"):
            href = "https://www.mobilezone.com.py" + (href if href.startswith("/") else "/" + href)

        img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
        if img_src and not img_src.startswith("http"):
            img_src = "https:" + img_src if img_src.startswith("//") else ""

        ext_id_match = re.search(r"/(\\d+)/?", href) or re.search(r"id=(\\d+)", href) or re.search(r"-p-(\\d+)", href)
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
