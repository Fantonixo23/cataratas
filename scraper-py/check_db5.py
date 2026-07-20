import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
from supabase import create_client
from collections import Counter
load_dotenv()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

# Get exact total
r = supabase.table("products").select("count", count="exact").limit(1).execute()
print(f"Total exact: {r.count}")

# Query all rows in chunks
all_data = []
offset = 0
while offset < 5000:
    chunk = supabase.table("products").select("store_origin").range(offset, offset+999).execute()
    if not chunk.data:
        break
    all_data.extend(chunk.data)
    offset += 1000
    if len(chunk.data) < 1000:
        break

cnt = Counter(p["store_origin"] for p in all_data)
print(f"Rows fetched: {len(all_data)}")
for s, c in cnt.most_common():
    print(f"  {s}: {c}")
