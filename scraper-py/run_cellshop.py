import sys, os, json, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stores.cellshop import scrape

# Run the scraper - will save progress periodically
try:
    prods = scrape()
    print(f"\nTotal scraped: {len(prods)}")
    
    # Save to file
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cellshop_products.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(prods, f, ensure_ascii=False, indent=2)
    print(f"Saved to {out}")
    
    # Upload
    from dotenv import load_dotenv
    from supabase import create_client
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
    supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    
    with_img = sum(1 for p in prods if p.get("image_url"))
    print(f"With images: {with_img}")
    
    for i in range(0, len(prods), 500):
        supabase.table("products").upsert(prods[i:i+500], on_conflict="store_origin,external_id").execute()
        print(f"  Uploaded batch {i//500 + 1}")
    print("Done")
except KeyboardInterrupt:
    print("\nInterrupted by user")
