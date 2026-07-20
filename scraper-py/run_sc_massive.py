import sys, os, json, math
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
from supabase import create_client
from stores import shoppingchina

load_dotenv()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

all_queries = [
    "apple", "samsung", "xiaomi", "motorola", "nokia", "huawei", "lg",
    "iphone 16", "iphone 17", "s25", "a16", "g84", "g86", "edge",
    "tv 32", "tv 43", "tv 50", "tv 55", "tv 65", "smart tv",
    "notebook lenovo", "notebook hp", "notebook dell", "notebook acer", "notebook asus",
    "macbook", "ipad", "airpods", "apple watch",
    "cafetera", "licuadora", "air fryer", "freidora", "microondas",
    "plancha", "aspiradora", "lavarropa", "heladera",
    "zapatilla", "zapato", "camisa", "remera", "pantalon", "vestido",
    "perfume", "colonia", "desodorante", "shampoo", "maquillaje",
    "juguete", "peluche", "lego", "bicicleta",
    "mueble", "silla", "mesa", "escritorio", "estante",
    "herramienta", "taladro", "martillo", "llave",
]

all_products = []
for q in all_queries:
    try:
        results = shoppingchina.scrape(q)
        all_products.extend(results)
    except:
        continue

print(f"Total raw: {len(all_products)}")

# Dedup manually
seen = set()
unique = []
for p in all_products:
    key = (p["store_origin"], p["external_id"])
    if key in seen:
        continue
    seen.add(key)
    # Clean NaN prices
    price = p.get("price")
    if price is not None and isinstance(price, float) and (math.isnan(price) or math.isinf(price)):
        price = None
    p["price"] = price
    unique.append(p)

print(f"Unique: {len(unique)}")

if unique:
    for i in range(0, len(unique), 500):
        supabase.table("products").upsert(unique[i:i+500], on_conflict="store_origin,external_id").execute()
    print(f"Subidos: {len(unique)}")
