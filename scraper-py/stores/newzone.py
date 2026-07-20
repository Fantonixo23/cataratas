import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "newzone"

# NewZone categories based on their site structure
URLS = [
    "https://newzone.com.py/",
    "https://newzone.com.py/categoria/celular",
    "https://newzone.com.py/categoria/informatica",
    "https://newzone.com.py/categoria/audio",
    "https://newzone.com.py/categoria/tv",
    "https://newzone.com.py/categoria/games",
    "https://newzone.com.py/categoria/accesorios",
]

def scrape(query: str = "") -> list[dict]:
    products = []
    seen = set()

    for url in URLS:
        try:
            soup = fetch_html(url, timeout=20)
        except Exception:
            continue

        found = 0
        for a in soup.select("a[href*='/producto/']"):
            href = a.get("href", "")
            if not href or href in seen:
                continue
            seen.add(href)

            name = a.get_text(strip=True)
            img = a.select_one("img")
            img_src = img.get("src") or img.get("data-src") or "" if img else ""

            if not name and not img_src:
                continue
            if not name:
                name = img.get("alt", "") if img else ""

            if not href.startswith("http"):
                href = "https://newzone.com.py" + href

            if img_src and not img_src.startswith("http"):
                img_src = "https:" + img_src if img_src.startswith("//") else ""

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
