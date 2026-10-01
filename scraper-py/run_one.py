import os
import sys
import time
import argparse

from dotenv import load_dotenv
from supabase import create_client

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

from run_catalog import assign_category


def upsert(records):
    uniq = {}
    for r in records:
        key = (r.get("store_origin"), str(r.get("external_id")))
        if key not in uniq:
            uniq[key] = r
    records = list(uniq.values())
    for i in range(0, len(records), 500):
        batch = records[i : i + 500]
        for attempt in range(6):
            try:
                sb.table("products").upsert(batch, on_conflict="store_origin,external_id").execute()
                break
            except Exception as e:
                print(f"  upsert fallo {attempt + 1}: {e}", flush=True)
                time.sleep(5 * (attempt + 1))


def load_existing(store):
    ids = set()
    start = 0
    while True:
        rows = sb.table("products").select("external_id").eq("store_origin", store).range(start, start + 999).execute().data
        for row in rows:
            ids.add(str(row.get("external_id")))
        if len(rows) < 1000:
            break
        start += 1000
    return ids


parser = argparse.ArgumentParser()
parser.add_argument("store")
args = parser.parse_args()

import importlib
mod = importlib.import_module(f"stores.{args.store}")
print(f"Corriendo {args.store}.scrape() ...", flush=True)
t0 = time.time()
records = mod.scrape("")
print(f"scrape termino en {time.time() - t0:.0f}s, {len(records)} productos", flush=True)

uniq = []
seen = set()
for p in records:
    key = (p.get("store_origin"), str(p.get("external_id")))
    if key in seen:
        continue
    seen.add(key)
    p["category"] = assign_category(p.get("name", ""))
    if isinstance(p.get("price"), float) and p["price"] != p["price"]:
        p["price"] = None
    uniq.append(p)

existing = load_existing(args.store)
new = [p for p in uniq if str(p.get("external_id")) not in existing]
print(f"{args.store}: {len(uniq)} unicos | nuevos: {len(new)}", flush=True)
if new:
    upsert(new)
print("DONE", flush=True)