import os
import re
import json
import sys
import time
import inspect
import importlib

from dotenv import load_dotenv
from supabase import create_client
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

from run_catalog import assign_category

STORE_MODULES = [
    "visaovip", "elegancia", "newzone", "oneclick", "topdek", "agatres",
    "lifebeach", "mobilezone", "atacadoconnect", "madridcenter", "tiendamovil",
    "megaelectronicos", "intershop", "guaranielectro", "electropar",
    "electronica", "cellshop", "bristol", "casarica",
]

# nissei NO esta en STORE_MODULES: esta bloqueado por Cloudflare desde esta IP
# (ver main.py:22). El modulo existe en stores/nissei.py y usa Chromium real
# via fetch_html_browser, pero solo funciona con SCRAPER_HEADLESS=0 y una IP
# no baneada. Para incluirlo:
#   1. SCRAPER_HEADLESS=0 python run_one.py nissei
#   2. si funciona, agregar "nissei" a STORE_MODULES
# Nota: shoppingchina tampoco va aqui; la maneja run_catalog.py por sitemap.

QUERIES = [
    "iphone", "samsung galaxy", "xiaomi", "notebook", "laptop", "playstation",
    "xbox", "tv", "audio", "parlante", "auricular", "audifono", "accesorios",
    "celular", "tablet", "smartwatch", "monitor", "teclado", "mouse", "ssd",
    "placa de video", "cargador", "cable", "power bank", "juego", "gaming",
    "pc gamer", "samsung", "motorola", "poco", "redmi", "nintendo",
    "impresora", "router", "memoria ram", "disco duro", "webcam", "gabinete",
]

CHECKPOINT = "checkpoint_all_stores.json"
EXPORT_DIR = "extraccion"
BATCH = 500


def load_existing_ids(store: str) -> set:
    ids = set()
    start = 0
    while True:
        r = supabase.table("products").select("external_id").eq("store_origin", store).range(start, start + 999).execute()
        rows = r.data
        for row in rows:
            ids.add(str(row.get("external_id")))
        if len(rows) < 1000:
            break
        start += 1000
    return ids


def upsert(records):
    uniq = {}
    for r in records:
        key = (r.get("store_origin"), str(r.get("external_id")))
        if key not in uniq:
            uniq[key] = r
    records = list(uniq.values())
    for i in range(0, len(records), BATCH):
        batch = records[i : i + BATCH]
        for attempt in range(6):
            try:
                supabase.table("products").upsert(batch, on_conflict="store_origin,external_id").execute()
                break
            except Exception as e:
                print(f"  upsert fallo (intento {attempt + 1}): {e}")
                time.sleep(5 * (attempt + 1))
        else:
            print("  upsert definitivamente fallido, batch descartado")


def run_store(name: str):
    mod = importlib.import_module(f"stores.{name}")
    records = []
    sig = inspect.signature(mod.scrape)
    params = list(sig.parameters.values())
    has_query = bool(params) and any(p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD for p in params)

    try:
        results = mod.scrape("")
        records.extend(results or [])
    except Exception as e:
        print(f"  {name} scrape('') error: {e}")

    if has_query:
        for q in QUERIES:
            try:
                r = mod.scrape(q)
                records.extend(r or [])
            except Exception:
                pass

    seen = set()
    uniq = []
    for p in records:
        key = (p.get("store_origin"), str(p.get("external_id")))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)

    for p in uniq:
        p["category"] = assign_category(p.get("name", ""))
        if isinstance(p.get("price"), float) and p["price"] != p["price"]:
            p["price"] = None

    return uniq


def main():
    ck = {}
    if os.path.exists(CHECKPOINT):
        with open(CHECKPOINT, "r", encoding="utf-8") as f:
            ck = json.load(f)
    done = set(ck.get("done", []))

    os.makedirs(EXPORT_DIR, exist_ok=True)
    all_records = []

    for name in STORE_MODULES:
        if name in done:
            print(f"SKIP {name} (ya completado)")
            continue
        print(f"==> {name} ...")
        uniq = run_store(name)
        existing = load_existing_ids(name)
        new = [p for p in uniq if str(p.get("external_id")) not in existing]
        print(f"  {name}: {len(uniq)} unicos | nuevos a subir: {len(new)}")
        if new:
            upsert(new)
        with open(os.path.join(EXPORT_DIR, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(uniq, f, ensure_ascii=False, default=str)
        all_records.extend(uniq)

        done.add(name)
        ck["done"] = list(done)
        with open(CHECKPOINT, "w", encoding="utf-8") as f:
            json.dump(ck, f, ensure_ascii=False)

    if all_records:
        df = pd.DataFrame(all_records).drop_duplicates(subset=["store_origin", "external_id"])
        df.to_csv("ultima_corrida_extra.csv", index=False)
        print(f"\nTOTAL extraido: {len(df)} productos | CSV: ultima_corrida_extra.csv")


if __name__ == "__main__":
    main()