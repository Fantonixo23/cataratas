import { createClient } from '@supabase/supabase-js';
import { getCategoriaBySlug, CATEGORIAS } from '@/lib/categorias';
import ProductCard from '@/components/ProductCard';
import Link from 'next/link';
import { notFound } from 'next/navigation';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function generateStaticParams() {
  return CATEGORIAS.map((cat) => ({ slug: cat.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const cat = getCategoriaBySlug(slug);
  if (!cat) return { title: 'Categoría no encontrada' };
  return {
    title: `${cat.name} — Catarata`,
    description: cat.description,
  };
}

export default async function CategoriaPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const cat = getCategoriaBySlug(slug);
  if (!cat) notFound();

  const { data: products } = await supabase
    .from('products')
    .select('name, price, image_url, source_url, store_origin, external_id, category')
    .eq('category', cat.name)
    .order('created_at', { ascending: false })
    .limit(50);

  return (
    <main className="max-w-5xl mx-auto p-6">
      <nav className="text-sm text-gray-400 mb-4">
        <Link href="/" className="hover:text-gray-600">Inicio</Link>
        <span className="mx-2">/</span>
        <span className="text-gray-800 font-medium">{cat.name}</span>
      </nav>

      <h1 className="text-2xl font-bold mb-1">{cat.icon} {cat.name}</h1>
      <p className="text-gray-500 text-sm mb-6">{cat.description}</p>

      {!products || products.length === 0 ? (
        <p className="text-gray-400">No hay productos en esta categoría aún.</p>
      ) : (
        <>
          <p className="text-sm text-gray-400 mb-4">{products.length} productos</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {products.map((p: any) => (
              <ProductCard key={p.external_id || p.id} product={p} showCategory />
            ))}
          </div>
        </>
      )}
    </main>
  );
}
