import os
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from supabase import create_client

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

import run_catalog as rc

CKPT = "backfill_ckpt.json"
WORKERS = 8
BATCH = 500
CHUNK = 40


def target_rows():
    rows = []
    start = 0
    while True:
        r = (
            sb.table("products")
            .select("source_url,external_id")
            .eq("store_origin", "shoppingchina")
            .or_("price.is.null,description.is.null")
            .range(start, start + 999)
            .execute()
        )
        data = r.data
        rows.extend(data)
        if len(data) < 1000:
            break
        start += 1000
    return rows


def load_ck():
    if os.path.exists(CKPT):
        with open(CKPT, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"done": []}


def save_ck(done, buffer, processed):
    with open(CKPT, "w", encoding="utf-8") as f:
        json.dump({"done": done, "buffer": buffer, "processed": processed}, f, ensure_ascii=False)


def main():
    ck = load_ck()
    done = set(ck.get("done", []))
    rows = [r for r in target_rows() if r["source_url"] not in done]
    print(f"filas objetivo: {len(rows)}", flush=True)

    buffer = []
    processed = len(done)
    idx = 0

    while idx < len(rows):
        chunk = rows[idx : idx + CHUNK]
        results = {}
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futures = {ex.submit(rc.fetch, r["source_url"]): r for r in chunk}
            for fut in as_completed(futures):
                r = futures[fut]
                try:
                    html = fut.result()
                    results[r["source_url"]] = rc.parse_product(html, r["source_url"])
                except Exception:
                    results[r["source_url"]] = None

        for r in chunk:
            url = r["source_url"]
            done.add(url)
            processed += 1
            prod = results.get(url)
            if prod:
                if not prod.get("category"):
                    prod["category"] = rc.assign_category(prod["name"])
                buffer.append(prod)

        if len(buffer) >= BATCH:
            rc.upsert(buffer)
            print(f"  +{len(buffer)} (procesados {processed})", flush=True)
            buffer = []
            save_ck(list(done), buffer, processed)

        idx += len(chunk)

    if buffer:
        rc.upsert(buffer)
        print(f"  +{len(buffer)} final", flush=True)
    save_ck(list(done), [], processed)
    print(f"BACKFILL FIN: {processed} filas procesadas", flush=True)


if __name__ == "__main__":
    main()