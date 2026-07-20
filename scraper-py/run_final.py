import sys, os, re, json, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
from supabase import create_client
from common import fetch_html, parse_price, polite_delay

load_dotenv()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

CATEGORY_RULES = [
    ("Celulares y Tablets", re.compile(r"iphone|ipad|smartphone|celular|tablet|samsung galaxy|xiaomi|moto g|poco |redmi ", re.I)),
    ("Informatica y Notebooks", re.compile(r"notebook|laptop|computador|pc |monitor|teclado|mouse|ssd|hd |memoria|ram|procesador|disco|gabinete|fuente|placa de video|accesorios pc", re.I)),
    ("Electronica y TVs", re.compile(r"tv |televisor|home theater|speaker|parlante|audio|hisense|samsung tv|lg ", re.I)),
    ("Videojuegos y Consolas", re.compile(r"playstation|xbox|nintendo|juego|game|gaming|gamer|consola|ps5|ps4|fifa", re.I)),
    ("Audio y Accesorios", re.compile(r"auricular|headphone|audifono|cargador|cable|funda|case|bateria|power bank|usb|hub |adaptador|bluetooth", re.I)),
    ("Perfumes y Cosmetica", re.compile(r"perfume|cosmetic|maquillaje|edp|eau de|fragancia|crema|shampoo|desodorante|makeup|labial", re.I)),
    ("Deportes y Fitness", re.compile(r"raqueta|beach tennis|padel|tenis|deporte|fitness", re.I)),
]

def assign_category(name):
    for cat_name, pattern in CATEGORY_RULES:
        if pattern.search(name):
            return cat_name
    return "Otros"

all_raw = []
seen = set()

# Lifebeach: scrape all products with pagination
lifebeach_cats = ["beach-tennis", "padel", "tenis", "acessorios", "roupas"]
for cat in lifebeach_cats:
    for page in range(1, 6):  # up to 5 pages
        url = f"https://www.lifebeach.com.py/categoria/{cat}?page={page}" if page > 1 else f"https://www.lifebeach.com.py/categoria/{cat}"
        try:
            soup = fetch_html(url, timeout=20)
        except:
            continue
        found = 0
        for card in soup.select(".product, .product-wrap, [class*=product]"):
            name_el = card.select_one(".product-name, [class*=name]")
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 3:
                continue
            price_el = card.select_one(".product-price, .price, .preco, [class*=price]")
            img_el = card.select_one("img")
            link_el = card.select_one("a[href*='/produto/']") or card.select_one(".product-name a") or card.select_one("a")
            href = link_el.get("href", "") if link_el else ""
            if href in seen:
                continue
            seen.add(href)
            if href and not href.startswith("http"):
                href = "https://www.lifebeach.com.py" + (href if href.startswith("/") else "/" + href)
            img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
            if img_src and not img_src.startswith("http"):
                img_src = "https:" + img_src if img_src.startswith("//") else ""
            ext_id_match = re.search(r"/(\d+)/?", href) or re.search(r"id=(\d+)", href)
            external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]
            all_raw.append({
                "name": name, "price": parse_price(price_el.get_text(strip=True) if price_el else None),
                "image_url": img_src or None, "source_url": href,
                "external_id": external_id, "store_origin": "lifebeach",
            })
            found += 1
        print(f"  lifebeach '{cat}' p.{page}: {found}")
        polite_delay(0.3, 0.5)

# Shopping China: expand queries for more variety
extra_queries = ["cargador", "funda", "audifonos", "parlante", "reloj", "mochila", "camara", "juguete", "ropa", "zapatilla"]
for q in extra_queries:
    try:
        from stores.shoppingchina import scrape as sc_scrape
        results = sc_scrape(q)
    except:
        continue
    new_count = 0
    for p in results:
        if p["source_url"] not in seen:
            seen.add(p["source_url"])
            all_raw.append(p)
            new_count += 1
    print(f"  shoppingchina '{q}': {new_count} new")
    polite_delay(0.3, 0.5)

# Newzone: try with different homepage paths
for path in ["/productos", "/catalogo", "/ofertas"]:
    url = f"https://newzone.com.py{path}"
    try:
        soup = fetch_html(url, timeout=15)
    except:
        continue
    found = 0
    for a in soup.select("a[href*='/producto/']"):
        href = a.get("href", "")
        if href in seen:
            continue
        seen.add(href)
        name = a.get_text(strip=True)
        img = a.select_one("img")
        img_src = img.get("src") or img.get("data-src") or "" if img else ""
        if not name and not img_src:
            continue
        if not href.startswith("http"):
            href = "https://newzone.com.py" + href
        if img_src and not img_src.startswith("http"):
            img_src = "https:" + img_src if img_src.startswith("//") else ""
        ext_id_match = re.search(r"/producto/(\d+)", href)
        external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", (name or ""))[:20]
        all_raw.append({
            "name": (name or img.get("alt", ""))[:200],
            "price": None, "image_url": img_src or None,
            "source_url": href, "external_id": external_id, "store_origin": "newzone",
        })
        found += 1
    print(f"  newzone '{path}': {found}")
    polite_delay(0.3, 0.5)

print(f"\nTotal raw: {len(all_raw)}")
if all_raw:
    df = pd.DataFrame(all_raw).drop_duplicates(subset=["store_origin", "external_id"])
    records = df.to_dict(orient="records")
    for r in records:
        r["category"] = assign_category(r.get("name", ""))
    for r in records:
        for k, v in r.items():
            if isinstance(v, float) and v != v:
                r[k] = None
    for i in range(0, len(records), 500):
        supabase.table("products").upsert(records[i:i+500], on_conflict="store_origin,external_id").execute()
    print(f"Subidos: {len(records)}")
