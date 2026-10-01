"""
Sube los productos scrapeados a Supabase.

Las tablas se crean con supabase-schema.sql (ejecutar en el SQL Editor de
Supabase). Este script solo escribe datos via la API REST.

Uso:
    python3 upload_to_supabase.py                    # sube output/productos.json
    python3 upload_to_supabase.py --limit 10
    python3 upload_to_supabase.py --file otro.json
"""

import argparse
import gzip
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

from categorias_shoppingchina import STORE_ID, catalogo_rows, categorizar

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE = os.path.join(HERE, "output", "productos.json")


def load_env():
    """Busca las claves en .env o .env.local (formato KEY=valor)."""
    env = {}
    for name in (".env", ".env.local"):
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


class SupabaseError(Exception):
    def __init__(self, status, body):
        self.status = status
        self.body = body
        try:
            parsed = json.loads(body)
            msg = parsed.get("message") or parsed.get("error") or body
            self.code = parsed.get("code")
        except json.JSONDecodeError:
            msg, self.code = body, None
        super().__init__(f"[{status}{' ' + self.code if self.code else ''}] {msg}")

    @property
    def missing_table(self):
        return self.code == "PGRST205" or "Could not find the table" in str(self.body)


def rest(method, url, key, body=None, prefer_return=False, merge=False):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    # PostgREST ignora ?on_conflict= si no viene resolution=merge-duplicates,
    # y en ese caso el INSERT falla por duplicado en vez de hacer upsert.
    prefer = []
    if merge:
        prefer.append("resolution=merge-duplicates")
    if prefer_return:
        prefer.append("return=representation")
    if prefer:
        headers["Prefer"] = ", ".join(prefer)
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raise SupabaseError(e.code, e.read().decode("utf-8", "ignore")) from None


def ensure_tables(url, key):
    """Verifica que products y categories existan antes de escribir."""
    rest_base = f"{url}/rest/v1"
    missing = []
    for table in ("categories", "products"):
        try:
            rest("GET", f"{rest_base}/{table}?select=*&limit=1", key)
        except SupabaseError as e:
            if e.missing_table:
                missing.append(table)
            else:
                raise
    if missing:
        print("\n!! Faltan tablas en Supabase: " + ", ".join(missing))
        print("   El SQL hay que correrlo en el dashboard:")
        print("   Supabase -> SQL Editor -> nuevo query -> Run")
        print("   (el archivo ya esta listo: supabase-schema.sql)\n")
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DEFAULT_FILE)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    env = load_env()
    url = env.get("NEXT_PUBLIC_SUPABASE_URL")
    key = env.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print("Faltan NEXT_PUBLIC_SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en .env")
        return 1

    rest_base = f"{url}/rest/v1"
    print(f"-> Conectando a {url}")

    if not ensure_tables(url, key):
        return 1

    with open(args.file, encoding="utf-8") as fh:
        payload = json.load(fh)
    products = payload["productos"] if isinstance(payload, dict) else payload
    if args.limit:
        products = products[: args.limit]

    good = [p for p in products if not p.get("error")]
    if len(good) != len(products):
        print(f"-> Omitiendo {len(products) - len(good)} productos con error")
    print(f"-> {len(good)} productos desde {os.path.basename(args.file)}")

    # 1) catalogos
    cats = catalogo_rows()
    rest(
        "POST",
        f"{rest_base}/categories?on_conflict=name",
        key,
        cats,
        prefer_return=True,
        merge=True,
    )
    print(f"-> Catalogos sincronizados: {len(cats)}")

    # 2) productos
    rows = []
    for p in good:
        categoria, sc_cat, sc_sub = categorizar(p.get("breadcrumb"))
        rows.append(
            {
                "external_id": p["external_id"],
                "store_origin": p.get("store_origin", STORE_ID),
                "name": p["name"],
                "price": p.get("price"),
                "currency": p.get("currency"),
                "image_url": p.get("image_url"),
                "source_url": p.get("source_url"),
                "brand": p.get("brand"),
                "category": categoria,
                "store_category": sc_cat,
                "store_subcategory": sc_sub,
                "available": p.get("available", True),
                "image_file": p.get("image_file"),
            }
        )

    saved = []
    batch_size = 500
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        res = rest(
            "POST",
            f"{rest_base}/products?on_conflict=store_origin,external_id",
            key,
            batch,
            prefer_return=True,
            merge=True,
        )
        saved.extend(res or [])
        print(f"-> Lote {i // batch_size + 1}: {len(res or [])} filas")

    print(f"-> Total guardado: {len(saved)}")

    # 3) verificacion
    total = rest("GET", f"{rest_base}/products?select=id", key) or []
    print(f"-> Verificacion: la tabla products tiene {len(total)} filas")

    with_img = rest("GET", f"{rest_base}/products?select=image_url&image_url=not.is.null", key) or []
    print(f"-> Filas con imagen: {len(with_img)}")

    priced = rest("GET", f"{rest_base}/products?select=price&price=not.is.null", key) or []
    print(f"-> Filas con precio: {len(priced)}")

    from collections import Counter

    cats_db = rest("GET", f"{rest_base}/products?select=category", key) or []
    dist = Counter(r["category"] for r in cats_db)
    print("\n-- Distribucion por categoria --")
    for c, n in dist.most_common():
        print(f"   {n:5d}  {c}")

    cats_tabla = rest("GET", f"{rest_base}/categories?select=name", key) or []
    print(f"\n-> Catalogos en la tabla categories: {len(cats_tabla)}")

    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
