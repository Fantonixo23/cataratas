import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
from supabase import create_client
from collections import Counter
load_dotenv()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

r = supabase.table("products").select("*", count="exact").range(0, 5000).execute()
cnt = Counter(p["store_origin"] for p in r.data)
for s, c in cnt.most_common():
    print(f"  {s}: {c}")
print(f"  TOTAL in response: {sum(cnt.values())}")
print(f"  COUNT exact: {r.count}")
