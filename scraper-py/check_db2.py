import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
from supabase import create_client
load_dotenv()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

stores = supabase.table("products").select("store_origin", count="exact").execute()
from collections import Counter
cnt = Counter(p["store_origin"] for p in stores.data)
for s, c in cnt.most_common():
    print(f"  {s}: {c}")
print(f"  TOTAL: {sum(cnt.values())}")
print(f"  COUNT: {stores.count}")
