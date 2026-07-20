import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("scraper-py/.env")
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

# Count total products with null/empty image
res = supabase.table("products").select("id, store_origin", count="exact").is_("image_url", "null").execute()
print(f"Sin image_url: {res.count}")
if res.data:
    store_counts = {}
    for r in res.data:
        s = r["store_origin"]
        store_counts[s] = store_counts.get(s, 0) + 1
    for s, c in sorted(store_counts.items(), key=lambda x: -x[1]):
        print(f"  {s}: {c}")
    print(f"  (mostradas {len(res.data)} de {res.count})")

# Show some without images
res2 = supabase.table("products").select("id, external_id, name, store_origin, image_url").is_("image_url", "null").limit(20).execute()
print("\nEjemplos sin imagen:")
for r in res2.data:
    print(f'  {r["store_origin"]:15s} | {r["external_id"][:25]:25s} | {r["name"][:50]}')
