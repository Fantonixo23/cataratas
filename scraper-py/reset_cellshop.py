import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_ROLE_KEY'])

resp = supabase.table('products').delete().eq('store_origin', 'cellshop').execute()
deleted = len(resp.data) if resp.data else 0
print(f'Eliminados: {deleted} productos de cellshop')

count = supabase.table('products').select('*', count='exact', head=True).execute()
print(f'Quedan: {count.count} (visaovip)')
