"""
Scraper del catalogo completo de Shopping China (Ciudad del Este).

Usa el sitemap.xml publico (declarado en robots.txt) para obtener TODAS las
URLs de producto, y despues parsea el JSON-LD schema.org/Product de cada
pagina para obtener nombre, SKU, precio, disponibilidad, marca e imagen.

Solo libreria estandar: no requiere pip install.

Uso:
    python3 scrape_shoppingchina.py                 # 10 productos (default)
    python3 scrape_shoppingchina.py --limit 100     # 100 productos
    python3 scrape_shoppingchina.py --offset 500    # arrancar desde el 500
    python3 scrape_shoppingchina.py --no-images     # solo URLs de imagen
    python3 scrape_shoppingchina.py --workers 6     # menos concurrencia
"""

import argparse
import gzip
import json
import os
import random
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding="utf-8")

BASE = "https://www.shoppingchina.com.py"
STORE_ID = "shoppingchina"
SITEMAP_URL = f"{BASE}/sitemap.xml"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "output")
IMG_DIR = os.path.join(OUT_DIR, "imagenes")
JSON_OUT = os.path.join(OUT_DIR, "productos.json")

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": UA,
    "Accept-Language": "es-PY,es;q=0.9",
    "Accept-Encoding": "gzip",
}

USER_AGENT = "CatarataBot/1.0 (scraper de catalogo; contacto: hola@catarata.shop)"

_politeness_lock = __import__("threading").Lock()
_last_request = [0.0]
MIN_GAP = 0.15


def _respect_gap():
    """Espacia los requests para no pegarle al servidor."""
    with _politeness_lock:
        wait = MIN_GAP - (time.monotonic() - _last_request[0])
        if wait > 0:
            time.sleep(wait)
        _last_request[0] = time.monotonic()


def fetch(url, timeout=30):
    """Devuelve (status, content_type, bytes). Sigue redirects."""
    _respect_gap()
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
        return resp.status, resp.headers.get("Content-Type"), data


def fetch_text(url, timeout=30):
    return fetch(url, timeout)[2].decode("utf-8", "ignore")


def polite_delay(min_s=1.5, max_s=4.0):
    time.sleep(random.uniform(min_s, max_s))


def get_catalogue_urls():
    """Lee el sitemap publico y devuelve las URLs de producto."""
    xml = fetch_text(SITEMAP_URL, timeout=60)
    urls = re.findall(
        r"<loc>(https://www\.shoppingchina\.com\.py/producto/[^<]+)</loc>", xml
    )
    seen = set()
    unique = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique


def extract_jsonld(html):
    m = re.search(
        r'<script type="application/ld\+json"[^>]*>\s*(\{.*?\})\s*</script>',
        html,
        re.S,
    )
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def extract_breadcrumb(html):
    """Devuelve la categoria real del producto desde el breadcrumb."""
    i = html.find('class ="breadcrumb"')
    if i < 0:
        return []
    segment = html[i : i + 600]
    crumbs = []
    for path, text in re.findall(r'href="(/[^"]*)"[^>]*>\s*([^<]+?)\s*<', segment):
        text = text.strip()
        # el primer crumb es el link a home ("/" con texto "Inicio"), se descarta
        if not text or path == "/":
            continue
        # solo primer y segundo nivel: /categoria y /categoria/subcategoria
        if path.count("/") > 2:
            continue
        if text not in crumbs:
            crumbs.append(text)
    return crumbs


def slugify_external_id(url, p):
    """El @id del JSON-LD es el SKU real de la tienda."""
    sku = str(p.get("@id") or "").strip()
    if sku:
        return sku
    m = re.search(r"-(\d+)$", url)
    if m:
        return m.group(1)
    return re.sub(r"[^a-zA-Z0-9]", "", url.rsplit("/", 1)[-1])[:32]


def save_image(url, sku):
    """Descarga la imagen del producto. Devuelve (bytes, nombre_archivo)."""
    try:
        status, ctype, data = fetch(url, timeout=45)
    except Exception:
        return None, None
    if not data or len(data) < 500:
        return None, None
    ext = ".png" if (ctype or "").startswith("image/png") else ".jpg"
    fname = f"{sku}{ext}"
    with open(os.path.join(IMG_DIR, fname), "wb") as fh:
        fh.write(data)
    return len(data), fname


def scrape_one(url, with_images=True):
    try:
        html = fetch_text(url)
    except Exception as e:
        return {"error": f"fetch: {type(e).__name__}: {e}", "source_url": url}

    p = extract_jsonld(html)
    if not p or not p.get("name"):
        return {"error": "sin JSON-LD Product", "source_url": url}

    offers = p.get("offers") or {}
    price_raw = offers.get("price")
    try:
        price = float(price_raw) if price_raw not in (None, "", "null") else None
    except (TypeError, ValueError):
        price = None

    image_url = p.get("image")
    if isinstance(image_url, list):
        image_url = image_url[0] if image_url else None
    if image_url and image_url.startswith("//"):
        image_url = "https:" + image_url

    sku = slugify_external_id(url, p)
    brand = p.get("brand") or {}
    if isinstance(brand, str):
        brand = {"name": brand}

    record = {
        "name": p.get("name"),
        "external_id": sku,
        "price": price,
        "currency": offers.get("priceCurrency"),
        "available": (offers.get("availability") or "").endswith("InStock"),
        "availability": (offers.get("availability") or "").split("/")[-1] or None,
        "brand": brand.get("name"),
        "breadcrumb": extract_breadcrumb(html),
        "image_url": image_url,
        "source_url": p.get("url") or url,
        "store_origin": STORE_ID,
    }

    if with_images and image_url:
        size, fname = save_image(image_url, sku)
        record["image_file"] = fname
        record["image_bytes"] = size
    else:
        record["image_file"] = None
        record["image_bytes"] = None

    return record


def main():
    ap = argparse.ArgumentParser(description="Scraper del catalogo de Shopping China")
    ap.add_argument("--limit", type=int, default=10, help="cuantos productos traer")
    ap.add_argument("--offset", type=int, default=0, help="desde cual empezar")
    ap.add_argument("--workers", type=int, default=8, help="requests en paralelo")
    ap.add_argument("--no-images", action="store_true", help="no descargar imagenes")
    ap.add_argument("--delay", type=float, default=1.5, help="min delay entre batches")
    args = ap.parse_args()

    os.makedirs(IMG_DIR, exist_ok=True)

    print(f"-> Leyendo sitemap: {SITEMAP_URL}")
    catalogue = get_catalogue_urls()
    print(f"-> Catalogo completo: {len(catalogue):,} productos\n")

    batch = catalogue[args.offset : args.offset + args.limit]
    if not batch:
        print("No hay URLs en ese rango.")
        return

    print(f"-> Trayendo {len(batch)} productos con {args.workers} workers...\n")

    t0 = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(scrape_one, u, not args.no_images): u for u in batch}
        for fut in as_completed(futures):
            results.append(fut.result())
            print("   .", end="", flush=True)
    elapsed = time.time() - t0
    print(f"\n-> Completado en {elapsed:.1f}s\n")

    # orden estable: como vinieron en el sitemap
    order = {u: i for i, u in enumerate(batch)}
    results.sort(key=lambda r: order.get(r.get("source_url"), 1 << 30))

    errors = [r for r in results if r.get("error")]
    ok = [r for r in results if not r.get("error")]
    completos = [
        r
        for r in ok
        if r.get("name") and r.get("price") is not None and r.get("image_file")
    ]

    with open(JSON_OUT, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "store_origin": STORE_ID,
                "total_catalogo": len(catalogue),
                "offset": args.offset,
                "limit": args.limit,
                "obtenidos": len(ok),
                "errores": len(errors),
                "productos": results,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )

    print(f"{'SKU':>9} | {'DISPON':8} | {'PRECIO':>10} | {'IMG':>7} | {'CATEGORIA':28} | NOMBRE")
    print("-" * 118)
    for r in results:
        if r.get("error"):
            print(f"{'ERROR':>9} | {r['error'][:100]}")
            continue
        precio = f"Gs {int(r['price']):,}" if r["price"] is not None else "s/precio"
        img = f"{round(r['image_bytes'] / 1024)}KB" if r.get("image_bytes") else "sin img"
        cat = " > ".join(r.get("breadcrumb", [])[:2])[:28]
        print(
            f"{r['external_id']:>9} | {r['availability'][:8]:8} | {precio:>10} | {img:>7} | {cat:28} | {r['name'][:44]}"
        )

    print("\n" + "=" * 60)
    print(f"Solicitados   : {len(batch)}")
    print(f"Obtenidos     : {len(ok)}")
    print(f"Completos     : {len(completos)}  (nombre + precio + imagen)")
    print(f"Errores       : {len(errors)}")
    print(f"Imagenes en   : {IMG_DIR}")
    print(f"Datos en      : {JSON_OUT}")
    print("=" * 60)

    if len(completos) == len(batch) and len(batch) > 0:
        print(f"\nAYO CHEFT!  PRODUCTOS {len(completos)} IMAAGENSS OBTENIDAS CON EXITO")
    else:
        print("\nIncompleto: revisar errores antes de subir a Supabase.")


if __name__ == "__main__":
    main()
