import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "elegancia"

MENUS = ["perfumes", "nicho", "cosmeticos", "maquillaje", "outlet", "arabes"]

def scrape(query: str = "") -> list[dict]:
    products = []
    seen_hrefs = set()

    for menu in MENUS:
        url = f"https://www.eleganciacompany.com/productos?menu_id={menu}"
        try:
            soup = fetch_html(url, timeout=20)
        except Exception:
            continue

        for a in soup.select("a[href*='/productos/']"):
            href = a.get("href", "")
            if not href or href in seen_hrefs:
                continue
            seen_hrefs.add(href)

            img = a.select_one("img")
            name = a.get_text(strip=True) or (img.get("alt", "") if img else "")
            if not name or len(name) < 3:
                continue
            if name in ("Codigo:", "Codigo", ""):
                continue

            if not href.startswith("http"):
                href = "https://www.eleganciacompany.com" + href

            img_src = img.get("src") or img.get("data-src") or "" if img else ""
            if img_src and not img_src.startswith("http"):
                img_src = "https:" + img_src if img_src.startswith("//") else ""

            ext_id_match = re.search(r"/(\d+)$", href)
            external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

            products.append({
                "name": name,
                "price": None,
                "image_url": img_src or None,
                "source_url": href,
                "external_id": external_id,
                "store_origin": STORE_ID,
            })

        polite_delay(0.5, 1.5)

    return products
