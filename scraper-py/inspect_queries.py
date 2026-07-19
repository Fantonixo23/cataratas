import sys
sys.stdout.reconfigure(encoding='utf-8')

from stores.cellshop import scrape

for q in ["iphone", "samsung", "notebook", "playstation", "xiaomi", "tv", "audifonos"]:
    results = scrape(q)
    # Get first 2 names
    names = [r["name"][:40] for r in results[:2]]
    print(f"{q:15s} → {len(results):2d} productos | ej: {names}")
