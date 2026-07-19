import os, sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_ROLE_KEY'])

for store in ['cellshop', 'visaovip']:
    data = supabase.table('products').select('external_id,name').eq('store_origin', store).order('created_at', desc=True).execute()
    print(f'\n=== {store} ({len(data.data)} products) ===')
    for p in data.data:
        is_num = p['external_id'].isdigit()
        marker = 'OK' if is_num else 'BAD'
        print(f'  [{marker}] {p["external_id"]} | {p["name"][:60]}')
