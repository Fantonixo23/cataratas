import { getCategoriaBySlug, CATEGORIAS } from '@/lib/categorias';
import CategorySection from '@/components/CategorySection';
import Link from 'next/link';
import { notFound } from 'next/navigation';

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

  return (
    <section className="p-6">
      <nav className="text-sm text-gray-400 mb-4">
        <Link href="/" className="hover:text-gray-600">Inicio</Link>
        <span className="mx-2">/</span>
        <span className="text-gray-800 font-medium">{cat.name}</span>
      </nav>

      <h1 className="text-2xl font-bold mb-1">{cat.icon} {cat.name}</h1>
      <p className="text-gray-500 text-sm mb-6">{cat.description}</p>

      <CategorySection categoria={cat} />
    </section>
  );
}
