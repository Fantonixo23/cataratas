import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
from supabase import create_client
from collections import Counter
load_dotenv()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

# Query in two batches
for offset in [0, 1000]:
    r = supabase.table("products").select("store_origin").range(offset, offset + 1999).execute()
    cnt = Counter(p["store_origin"] for p in r.data)
    print(f"Rows {offset}-{offset+len(r.data)-1}:")
    for s, c in cnt.most_common():
        print(f"  {s}: {c}")
    print(f"  Count: {len(r.data)}")
    print()

# Get exact total
r = supabase.table("products").select("count", count="exact").limit(1).execute()
print(f"Total exact: {r.count}")
