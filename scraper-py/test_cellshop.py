import sys
sys.stdout.reconfigure(encoding='utf-8')

from stores.cellshop import scrape

results = scrape("iphone")
print(f"Productos encontrados: {len(results)}")
for p in results[:3]:
    print(f"\n  {p['name']}")
    print(f"  Precio: {p['price']} Gs.")
    print(f"  Imagen: {p['image_url'][:60]}...")
    print(f"  ID: {p['external_id']}")
