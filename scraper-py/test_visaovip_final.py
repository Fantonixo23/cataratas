import sys
sys.stdout.reconfigure(encoding='utf-8')

from stores.visaovip import scrape

results = scrape()
print(f"Productos: {len(results)}")
for r in results[:3]:
    name = r["name"][:50]
    price = r["price"]
    img = r["image_url"][:50] if r["image_url"] else "N/A"
    print(f"  {name} | {price} | {img}")
