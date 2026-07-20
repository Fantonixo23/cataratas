import { createClient } from '@supabase/supabase-js';
import SearchResults from './SearchResults';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export default async function BuscarPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const q = (await searchParams).q || '';
  const { data: products } = await supabase
    .from('products')
    .select('name, price, image_url, source_url, store_origin, external_id, category')
    .order('created_at', { ascending: false })
    .limit(2000);

  return (
    <main className="max-w-5xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-1">
        {q ? `Resultados para "${q}"` : 'Todos los productos'}
      </h1>
      <SearchResults query={q} products={products || []} />
    </main>
  );
}
