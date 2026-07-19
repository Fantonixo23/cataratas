import os
import re
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"],
)

CATEGORY_RULES = [
    ("Celulares y Tablets", re.compile(r"iphone|ipad|smartphone|celular|tablet|samsung galaxy|xiaomi|moto g|poco |redmi ", re.I)),
    ("Informática y Notebooks", re.compile(r"notebook|laptop|computador|pc |monitor|teclado|mouse|ssd|hd |memoria|ram|procesador|disco|gabinete|fuente|placa de video|accesorios pc", re.I)),
    ("Electrónica y TVs", re.compile(r"tv |televisor|home theater|speaker|parlante|audio|home theater|hisense|samsung tv|lg ", re.I)),
    ("Videojuegos y Consolas", re.compile(r"playstation|xbox|nintendo|juego|game|gaming|gamer|consola|ps5|ps4|fifa", re.I)),
    ("Audio y Accesorios", re.compile(r"auricular|headphone|audifono|cargador|cable|funda|case|bateria|power bank|usb|hub |adaptador|bluetooth", re.I)),
]


def assign_category(name: str) -> str:
    for cat_name, pattern in CATEGORY_RULES:
        if pattern.search(name):
            return cat_name
    return "Otros"


def main():
    # Agregar columna category si no existe
    try:
        supabase.rpc("add_category_column").execute()
    except:
        try:
            supabase.table("products").update({"category": None}).eq("category", "__dummy__").execute()
        except:
            pass

    # Obtener todos los productos sin categoría
    res = supabase.table("products").select("id, name, category").is_("category", "null").execute()
    products = res.data
    print(f"Productos sin categoría: {len(products)}")

    for p in products:
        cat = assign_category(p["name"])
        supabase.table("products").update({"category": cat}).eq("id", p["id"]).execute()
        print(f"  {p['name'][:40]:40s} → {cat}")

    # Mostrar resumen
    res2 = supabase.table("products").select("category").execute()
    cats = {}
    for p in res2.data:
        c = p.get("category") or "Sin categoría"
        cats[c] = cats.get(c, 0) + 1
    print("\n--- Resumen ---")
    for c, n in sorted(cats.items()):
        print(f"  {c}: {n} productos")


if __name__ == "__main__":
    main()
