import os
import re
import json
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

from stores import cellshop, visaovip

load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"],
)

SCRAPERS = [cellshop]
QUERIES = ["iphone", "samsung galaxy", "notebook", "playstation", "xiaomi", "tv", "audio", "accesorios"]
FIXED_SCRAPERS = [visaovip]

CATEGORY_RULES = [
    ("Celulares y Tablets", re.compile(r"iphone|ipad|smartphone|celular|tablet|samsung galaxy|xiaomi|moto g|poco |redmi ", re.I)),
    ("Informática y Notebooks", re.compile(r"notebook|laptop|computador|pc |monitor|teclado|mouse|ssd|hd |memoria|ram|procesador|disco|gabinete|fuente|placa de video|accesorios pc", re.I)),
    ("Electrónica y TVs", re.compile(r"tv |televisor|home theater|speaker|parlante|audio|hisense|samsung tv|lg ", re.I)),
    ("Videojuegos y Consolas", re.compile(r"playstation|xbox|nintendo|juego|game|gaming|gamer|consola|ps5|ps4|fifa", re.I)),
    ("Audio y Accesorios", re.compile(r"auricular|headphone|audifono|cargador|cable|funda|case|bateria|power bank|usb|hub |adaptador|bluetooth", re.I)),
]


def assign_category(name: str) -> str:
    for cat_name, pattern in CATEGORY_RULES:
        if pattern.search(name):
            return cat_name
    return "Otros"


def sync_to_supabase(records: list[dict]):
    batch_size = 500
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        supabase.table("products").upsert(batch, on_conflict="store_origin,external_id").execute()
    print(f"Subidos a Supabase: {len(records)} productos")


def run_all():
    all_products = []

    for store_module in SCRAPERS:
        for query in QUERIES:
            try:
                results = store_module.scrape(query)
                print(f"{store_module.STORE_ID} / '{query}': {len(results)} productos")
                all_products.extend(results)
            except Exception as e:
                print(f"Error en {store_module.STORE_ID} con '{query}': {e}")

    for store_module in FIXED_SCRAPERS:
        try:
            results = store_module.scrape()
            print(f"{store_module.STORE_ID} (home): {len(results)} productos")
            all_products.extend(results)
        except Exception as e:
            print(f"Error en {store_module.STORE_ID}: {e}")

    if not all_products:
        print("No se obtuvo ningún producto.")
        return []

    df = pd.DataFrame(all_products)
    df = df.drop_duplicates(subset=["store_origin", "external_id"])
    df.to_csv("ultima_corrida.csv", index=False)

    records = df.to_dict(orient="records")

    # Asignar categoría a cada producto
    for r in records:
        r["category"] = assign_category(r.get("name", ""))

    # Convertir NaN a None para que JSON no falle
    for r in records:
        for k, v in r.items():
            if isinstance(v, float) and (v != v):  # NaN check
                r[k] = None

    with open("ultima_corrida.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, default=str)

    print(f"\nTotal: {len(records)} productos únicos")

    sync_to_supabase(records)

    return records


if __name__ == "__main__":
    records = run_all()
    print("\n--- PRIMEROS 3 ---")
    for r in records[:3]:
        print(f"  [{r['store_origin']}] {r['name']} - ${r['price']} - {r['image_url'][:50] if r['image_url'] else 'N/A'}")
