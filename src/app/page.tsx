import { createClient } from '@supabase/supabase-js';
import ProductCard from '@/components/ProductCard';
import HeroCarousel from '@/components/HeroCarousel';
import { CATEGORIAS } from '@/lib/categorias';
import Link from 'next/link';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export default async function Home() {
  const { data: allProducts } = await supabase
    .from('products')
    .select('name, price, image_url, source_url, store_origin, external_id, category')
    .order('created_at', { ascending: false })
    .limit(50);

  const sections = CATEGORIAS.map((cat) => {
    const items = (allProducts || []).filter((p: any) => p.category === cat.name).slice(0, 4);
    return { ...cat, items };
  }).filter((s) => s.items.length > 0);

  return (
    <main className="max-w-5xl mx-auto p-6">
      <div className="mb-8">
        <HeroCarousel />
      </div>

      <h1 className="text-2xl font-bold mb-1">Productos destacados</h1>
      <p className="text-gray-500 text-sm mb-8">
        Usá el buscador de arriba o navegá por categorías
      </p>

      <div className="space-y-10">
        {sections.map((section) => (
          <section key={section.slug}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">
                {section.icon} {section.name}
              </h2>
              <Link
                href={`/categoria/${section.slug}`}
                className="text-sm text-blue-600 hover:underline"
              >
                Ver todos
              </Link>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {section.items.map((p: any) => (
                <ProductCard key={p.external_id || p.id} product={p} />
              ))}
            </div>
          </section>
        ))}
      </div>
    </main>
  );
}
