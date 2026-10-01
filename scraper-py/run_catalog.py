import os
import re
import json
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from curl_cffi import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

BASE = "https://www.shoppingchina.com.py"
URL_FILTER = re.compile(r"/producto/")
STORE = "shoppingchina"
CHECKPOINT = "checkpoint_shoppingchina.json"

WORKERS = 12
MAX_ATTEMPTS = 3
RETRY_SLEEP = 1.5
BATCH = 500
PARSE_CHUNK = 40

CATEGORY_RULES = [
    ("Celulares y Tablets", re.compile(r"iphone|ipad|smartphone|celular|tablet|samsung galaxy|xiaomi|moto g|poco |redmi ", re.I)),
    ("Informatica y Notebooks", re.compile(r"notebook|laptop|computador|pc |monitor|teclado|mouse|ssd|hd |memoria|ram|procesador|disco|gabinete|fuente|placa de video|accesorios pc", re.I)),
    ("Electronica y TVs", re.compile(r"tv |televisor|home theater|speaker|parlante|audio|hisense|samsung tv|lg ", re.I)),
    ("Videojuegos y Consolas", re.compile(r"playstation|xbox|nintendo|juego|game|gaming|gamer|consola|ps5|ps4|fifa", re.I)),
    ("Audio y Accesorios", re.compile(r"auricular|headphone|audifono|cargador|cable|funda|case|bateria|power bank|usb |hub |adaptador|bluetooth", re.I)),
]


def assign_category(name: str) -> str:
    for cat, pattern in CATEGORY_RULES:
        if pattern.search(name):
            return cat
    return "Otros"


def fetch(url: str, timeout=15) -> str:
    last = None
    for _ in range(MAX_ATTEMPTS):
        try:
            r = requests.get(url, impersonate="chrome136", timeout=timeout)
            if r.status_code == 200:
                return r.text
            last = RuntimeError(f"http {r.status_code}")
        except Exception as e:
            last = e
        time.sleep(RETRY_SLEEP)
    raise RuntimeError(f"fallo {url}: {last}")


def load_sitemap() -> list[str]:
    text = fetch(BASE + "/sitemap.xml", 40)
    urls = re.findall(r"<loc>(.*?)</loc>", text)
    return [u for u in urls if URL_FILTER.search(u)]


def parse_product(html: str, url: str):
    soup = BeautifulSoup(html, "html.parser")
    jsonld = None
    for s in soup.select('script[type="application/ld+json"]'):
        try:
            d = json.loads(s.get_text())
            if isinstance(d, dict) and str(d.get("@type", "")).lower() == "product":
                jsonld = d
                break
            if isinstance(d, list):
                d = next((x for x in d if isinstance(x, dict) and str(x.get("@type", "")).lower() == "product"), None)
                if d:
                    jsonld = d
                    break
        except Exception:
            continue

    name = None
    price = None
    img = None
    external_id = None
    description = None
    category = None
    brand = None

    if jsonld:
        name = jsonld.get("name")
        offers = jsonld.get("offers") or {}
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        raw_price = offers.get("price")
        try:
            price = float(raw_price)
        except (TypeError, ValueError):
            price = None
        img_def = jsonld.get("image")
        img = img_def if isinstance(img_def, str) else (img_def[0] if isinstance(img_def, list) and img_def else None)
        description = jsonld.get("description") or ""
        cat = jsonld.get("category")
        if isinstance(cat, str):
            category = cat
        brand = jsonld.get("brand")
        if isinstance(brand, dict):
            brand = brand.get("name")
        if not isinstance(brand, str):
            brand = None
        if not external_id:
            external_id = jsonld.get("@id")

    if not name:
        h1 = soup.select_one("h1")
        name = h1.get_text(strip=True) if h1 else None
    if not name:
        title = soup.title.string if soup.title else None
        if title:
            name = title.split("|")[0].strip()

    if not name or len(name) < 4:
        return None

    if not external_id:
        m = re.search(r"-(\d+)$", url)
        external_id = m.group(1) if m else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

    if not img:
        og = soup.select_one('meta[property="og:image"]')
        if og and og.get("content"):
            img = og["content"]
    if not img:
        for i in soup.select("img"):
            s = i.get("src") or i.get("data-src") or ""
            low = s.lower()
            if s.startswith("http") and "active_storage" in low and "logo" not in low:
                img = s
                break
    if not img:
        for i in soup.select("img"):
            s = i.get("src") or i.get("data-src") or ""
            low = s.lower()
            if s.startswith("http") and "logo" not in low and "menu" not in low and "icon" not in low and ".svg" not in low:
                img = s
                break
    if not img:
        return None

    if not description:
        desc_el = soup.select_one('meta[name="description"]')
        if desc_el and desc_el.get("content"):
            description = desc_el["content"]

    # Breadcrumb crudo del sitio, ej: "Inicio > Electrónicos > Accesorios".
    # No se usa directo: src/lib/categorias.ts tiene 13 slugs distintos y
    # /categoria/[slug] no encontraria estos productos.
    breadcrumb_raw = ""
    crumbs = [a.get_text(strip=True) for a in soup.select('[class*="breadcrumb"] a, nav[class*="breadcrumb"] a')]
    if crumbs:
        breadcrumb_raw = " > ".join(c for c in crumbs if c)

    # Se conserva el ultimo segmento con contenido util ("Accesorios"), y si
    # no hay breadcrumb se cae a las reglas por nombre.
    category_clean = normalize_category(category, breadcrumb_raw) or assign_category(name)

    return {
        "name": name.strip(),
        "price": price,
        "image_url": img or None,
        "source_url": url,
        "external_id": str(external_id),
        "store_origin": STORE,
        "description": (description or "")[:2000],
        "brand": brand,
        "category": category_clean,
        "category_raw": category or "",
    }


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
            raise RuntimeError("upsert fallo tras 6 intentos")


def load_existing_ids() -> set[str]:
    ids = set()
    start = 0
    while True:
        r = supabase.table("products").select("external_id").eq("store_origin", STORE).range(start, start + 999).execute()
        rows = r.data
        for row in rows:
            ids.add(str(row.get("external_id")))
        if len(rows) < 1000:
            break
        start += 1000
    return ids


def product_id_from_url(url: str):
    m = re.search(r"-(\d+)$", url)
    return m.group(1) if m else None


def load_checkpoint():
    if os.path.exists(CHECKPOINT):
        with open(CHECKPOINT, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"done": {}, "all": None}


def save_checkpoint(ck, buffer, total_parsed):
    ck["products_parsed"] = total_parsed
    ck["buffer"] = buffer
    with open(CHECKPOINT, "w", encoding="utf-8") as f:
        json.dump(ck, f, ensure_ascii=False)


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    ck = load_checkpoint()
    if not ck.get("all"):
        print("Cargando sitemap...")
        all_urls = load_sitemap()
        ck["all"] = all_urls
        print(f"sitemap: {len(all_urls)} productos")
    else:
        all_urls = ck["all"]
        print(f"sitemap (del checkpoint): {len(all_urls)}")

    buffer = list(ck.get("buffer") or [])
    if buffer:
        print(f"Recuperando {len(buffer)} productos pendientes del checkpoint...")
        upsert(buffer)
        buffer = []
        print("pendientes recuperados OK")

    pending = [u for u in all_urls if u not in ck["done"]]
    print("Cargando ids ya en DB para saltar productos commiteados...")
    existing = load_existing_ids()
    before = len(pending)
    pending = [u for u in pending if product_id_from_url(u) not in existing]
    print(f"skip por ids ya en DB: {before - len(pending)} evitados")
    if limit:
        pending = pending[:limit]
        print(f"MODO PRUEBA: procesando solo {len(pending)}")
    print(f"pendientes: {len(pending)} | hechos previos: {len(ck['done'])}")

    total_parsed = len(ck["done"])
    idx = 0

    while idx < len(pending):
        chunk = pending[idx : idx + PARSE_CHUNK]
        results = {}
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futures = {ex.submit(fetch, u): u for u in chunk}
            for fut in as_completed(futures):
                u = futures[fut]
                try:
                    html = fut.result()
                    results[u] = parse_product(html, u)
                except Exception:
                    results[u] = None

        for u in chunk:
            prod = results.get(u)
            ck["done"][u] = True
            total_parsed += 1
            if prod:
                if not prod.get("category"):
                    prod["category"] = assign_category(prod["name"])
                buffer.append(prod)

        if len(buffer) >= BATCH:
            upsert(buffer)
            print(f"+{len(buffer)} (parsed {total_parsed})")
            buffer = []
            save_checkpoint(ck, buffer, total_parsed)

        if idx % (PARSE_CHUNK * 5) == 0:
            save_checkpoint(ck, buffer, total_parsed)
            print(f"...checkpoint parsed={total_parsed} pendientes_buffer={len(buffer)}")

        idx += len(chunk)

    if buffer:
        upsert(buffer)
        print(f"+{len(buffer)} final")
    save_checkpoint(ck, [], total_parsed)

    print(f"\nFIN: {total_parsed} URLs procesadas de {len(all_urls)}")


if __name__ == "__main__":
    main()