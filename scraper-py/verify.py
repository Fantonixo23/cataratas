import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_ROLE_KEY'])

data = supabase.table('products').select('external_id,name,store_origin').limit(10).order('created_at', desc=True).execute()
print(f'Total: {len(data.data)} productos (10 mostrados)')
print()
for p in data.data:
    print(f'  [{p["store_origin"]}] external_id={p["external_id"]} | {p["name"][:60]}')
