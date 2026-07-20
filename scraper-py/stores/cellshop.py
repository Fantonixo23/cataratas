import re, time, json, os, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from common import fetch_html, parse_price

STORE_ID = "cellshop"
BASE = "https://cellshop.com.py"

TECH_CATEGORIES = [
    ("Informatica", 415),
    ("Celulares_Telefonia", 694),
    ("Apple", 1015),
    ("Electronicos", 307),
    ("Accesorios_Tecnologia", 13),
    ("Tablets", 682),
    ("Camaras_Filmadoras", 1054),
    ("Electrodomesticos", 304),
    ("Automotivo", 94),
    ("Vigilancia", 1060),
]

def resolve_img(src: str) -> str:
    if not src:
        return ""
    if src.startswith("http"):
        return src
    if src.startswith("//"):
        return "https:" + src
    return BASE + "/" + src.lstrip("/")

def fetch_page(cat_id: int, page: int) -> list[dict]:
    url = f"{BASE}/todos-los-departamentos/tecnologia?cat={cat_id}&p={page}"
    try:
        soup = fetch_html(url, timeout=30)
        if not soup:
            return []
    except Exception:
        return []

    products = []
    for card in soup.select(".product-item"):
        name_el = card.select_one(".product-item-link")
        price_el = card.select_one(".price")
        img_el = card.select_one("img")
        link_el = card.select_one("a.product-item-link")

        if not name_el or not link_el:
            continue

        name = name_el.get_text(strip=True)
        href = link_el.get("href", "")
        if not href or not name:
            continue

        img_src = ""
        if img_el:
            img_src = img_el.get("src") or img_el.get("data-src") or ""
        img_src = resolve_img(img_src)

        id_match = re.search(r"/id/(\d+)", href)
        if not id_match:
            id_match = re.search(r"/(\d+)-[^/]+/?$", href)
        external_id = id_match.group(1) if id_match else href.rstrip("/").split("/")[-1]

        products.append({
            "name": name,
            "price": parse_price(price_el.get_text(strip=True) if price_el else None),
            "image_url": img_src or None,
            "source_url": href,
            "external_id": external_id,
            "store_origin": STORE_ID,
        })

    return products

def scrape_category(label: str, cat_id: int) -> list[dict]:
    products = []
    seen_local = set()
    page = 1

    with ThreadPoolExecutor(max_workers=8) as executor:
        while True:
            # Submit next batch of pages in parallel
            futures = {}
            for p in range(page, page + 8):
                futures[executor.submit(fetch_page, cat_id, p)] = p

            any_data = False
            for future in as_completed(futures):
                p = futures[future]
                batch = future.result()
                if batch:
                    any_data = True
                    for prod in batch:
                        key = (prod["external_id"], prod["store_origin"])
                        if key not in seen_local:
                            seen_local.add(key)
                            products.append(prod)

            print(f".", end="", flush=True)

            if not any_data:
                break

            page += 8
            time.sleep(0.3)

    return products

def scrape(query: str = "") -> list[dict]:
    all_products = []
    seen_global = set()

    for label, cat_id in TECH_CATEGORIES:
        print(f"cellshop {label}: ", end="", flush=True)
        batch = scrape_category(label, cat_id)

        new_count = 0
        for p in batch:
            key = (p["external_id"], p["store_origin"])
            if key not in seen_global:
                seen_global.add(key)
                all_products.append(p)
                new_count += 1

        print(f" {len(batch)} items, {new_count} new")
        
        # Periodic save
        if len(all_products) > 0 and len(all_products) % 5000 < 500:
            print(f"  (saved checkpoint: {len(all_products)} total)")

    print(f"cellshop total: {len(all_products)} unique products")
    return all_products
