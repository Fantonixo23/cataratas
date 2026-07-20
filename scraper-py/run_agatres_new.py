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

all_products = []

# Skip pages 1-82 (already in DB), scrape 83-127
for page in range(83, 128):
    url = f"https://agatres.co/es/productos/page/{page}/"
    try:
        soup = fetch_html(url, timeout=30)
    except Exception as e:
        print(f"  page {page}: ERROR {e}")
        continue

    found = 0
    for card in soup.select(".product, [class*=product]"):
        name_el = card.select_one("h2 a, h3 a, .product-title a, .woocommerce-loop-product__title, .wd-entities-title a")
        if not name_el:
            continue
        name = name_el.get_text(strip=True)
        if not name or len(name) < 5:
            continue
        price_el = card.select_one(".price, .amount, .preco, .woocommerce-Price-amount")
        img_el = card.select_one("img")
        link_el = name_el if name_el.name == "a" else card.select_one("a[href*='/es/producto/']")
        if not link_el:
            continue
        href = link_el.get("href", "")
        if not href.startswith("http"):
            href = "https://agatres.co" + href
        img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
        if img_src and not img_src.startswith("http"):
            img_src = "https:" + img_src if img_src.startswith("//") else ""
        ext_id_match = re.search(r"/producto/([^/]+)", href) or re.search(r"/(\d+)/?", href) or re.search(r"p=(\d+)", href)
        external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]
        all_products.append({
            "name": name,
            "price": parse_price(price_el.get_text(strip=True) if price_el else None),
            "image_url": img_src or None,
            "source_url": href,
            "external_id": external_id,
            "store_origin": "agatres",
        })
        found += 1

    print(f"  page {page}: {found} productos")
    if found == 0:
        polite_delay(0.3, 0.5)
        continue
    polite_delay(0.5, 1.0)

print(f"\nTotal new raw: {len(all_products)}")

if all_products:
    df = pd.DataFrame(all_products)
    df = df.drop_duplicates(subset=["store_origin", "external_id"])
    records = df.to_dict(orient="records")
    for r in records:
        r["category"] = assign_category(r.get("name", ""))
    for r in records:
        for k, v in r.items():
            if isinstance(v, float) and v != v:
                r[k] = None
    batch_size = 500
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        supabase.table("products").upsert(batch, on_conflict="store_origin,external_id").execute()
    print(f"Subidos a Supabase: {len(records)} productos")
