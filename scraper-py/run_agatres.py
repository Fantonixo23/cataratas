import os, sys, re, json, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
from supabase import create_client
from stores import agatres

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

results = agatres.scrape("")
print(f"Agatres: {len(results)} productos")

if results:
    df = pd.DataFrame(results)
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
