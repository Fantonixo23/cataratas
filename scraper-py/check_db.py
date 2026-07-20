import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
from supabase import create_client
load_dotenv()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
# Get exact count
r = supabase.table("products").select("count", count="exact").limit(1).execute()
print(f"Total exact: {r.count}")

# Get store distribution
r2 = supabase.table("products").select("store_origin", count="exact").limit(5000).execute()
from collections import Counter
cnt = Counter(p.get("store_origin","?") for p in r2.data)
print(f"Rows returned: {len(r2.data)}")
for s, c in cnt.most_common():
    print(f"  {s}: {c}")
