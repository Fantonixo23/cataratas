import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_ROLE_KEY'])

resp = supabase.table('products').delete().eq('store_origin', 'cellshop').not_.like('external_id', '%[0-9]%').execute()
deleted = len(resp.data) if resp.data else 0
print(f'Eliminados: {deleted} productos viejos')

count = supabase.table('products').select('*', count='exact', head=True).execute()
print(f'Total productos ahora: {count.count}')

data = supabase.table('products').select('external_id,name').eq('store_origin', 'cellshop').limit(5).execute()
for p in data.data:
    print(f'  {p["external_id"]}: {p["name"][:50]}')
