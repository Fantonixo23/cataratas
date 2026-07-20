import { createClient } from '@supabase/supabase-js';
import ProductCard from '@/components/ProductCard';
import HeroCarousel from '@/components/HeroCarousel';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export default async function Home() {
  const { data: products } = await supabase
    .from('products')
    .select('name, price, image_url, source_url, store_origin, external_id, category')
    .order('created_at', { ascending: false })
    .limit(20);

  return (
    <section className="py-6">
      <div className="mb-8">
        <HeroCarousel />
      </div>

      <h1 className="text-2xl font-bold mb-1">Productos destacados</h1>
      <p className="text-gray-500 text-sm mb-8">
        Usá el buscador de arriba o navegá por categorías
      </p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {(products || []).map((p: any) => (
          <ProductCard key={p.external_id || p.id} product={p} />
        ))}
      </div>
    </section>
  );
}
