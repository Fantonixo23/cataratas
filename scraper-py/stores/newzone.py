import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "newzone"
BASE = "https://newzone.com.py"

URLS = [
    BASE + "/",
    BASE + "/categoria/celular",
    BASE + "/categoria/informatica",
    BASE + "/categoria/audio",
    BASE + "/categoria/tv",
    BASE + "/categoria/games",
    BASE + "/categoria/accesorios",
]

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

def scrape(query: str = "") -> list[dict]:
    products = []
    seen = set()

    for url in URLS:
        try:
            soup = fetch_html(url, timeout=20)
        except Exception:
            continue

        found = 0
        for card in soup.select(".product, [class*=product]"):
            link_el = card.select_one("a[href*='/producto/']")
            if not link_el:
                continue
            href = resolve_href(link_el.get("href", ""))
            if href in seen:
                continue
            seen.add(href)

            name = link_el.get_text(strip=True)

            img_el = card.select_one("img")
            img_src = ""
            if img_el:
                img_src = img_el.get("src") or img_el.get("data-src") or ""

            if not name and not img_src:
                continue
            if not name:
                name = img_el.get("alt", "") if img_el else ""

            img_src = resolve_img(img_src)

            ext_id_match = re.search(r"/producto/(\d+)", href)
            external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

            products.append({
                "name": name.strip() if name else "",
                "price": None,
                "image_url": img_src or None,
                "source_url": href,
                "external_id": external_id,
                "store_origin": STORE_ID,
            })
            found += 1

        print(f"  newzone '{url.split('/')[-1] or 'home'}': {found} productos")
        polite_delay(0.5, 1.0)

    return products
