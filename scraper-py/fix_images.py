import sys, os, math
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
from supabase import create_client
from stores import topdek, newzone, lifebeach, casarica, electropar

load_dotenv()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

def upsert(records, label):
    total = len(records)
    with_img = sum(1 for r in records if r.get("image_url"))
    print(f"{label}: {total} productos, {with_img} con imagen")
    if not records:
        return
    # Dedup by store_origin+external_id
    seen = set()
    unique = []
    for r in records:
        key = (r["store_origin"], r["external_id"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    if len(unique) < len(records):
        print(f"  Duplicados eliminados: {len(records) - len(unique)}")
    for i in range(0, len(unique), 500):
        supabase.table("products").upsert(unique[i:i+500], on_conflict="store_origin,external_id").execute()
    print(f"  Subidos: {len(unique)}")

# topdek
upsert(topdek.scrape(), "topdek")

# newzone
upsert(newzone.scrape(), "newzone")

# lifebeach
all_lb = []
for q in ["beach", "tenis", "padel", "roupa", "acessorio"]:
    all_lb.extend(lifebeach.scrape(q))
upsert(all_lb, "lifebeach")

# casarica
all_ca = []
for q in ["celular", "tv", "notebook", "perfume", "zapatilla", "juguete", "herramienta", "cama", "mueble", "cocina"]:
    all_ca.extend(casarica.scrape(q))
upsert(all_ca, "casarica")

# electropar
all_ep = []
for q in ["celular", "tv", "audio", "linea blanca", "cocina", "herramienta"]:
    all_ep.extend(electropar.scrape(q))
upsert(all_ep, "electropar")

print("Listo")
