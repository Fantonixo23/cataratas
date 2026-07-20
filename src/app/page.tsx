import HeroCarousel from '@/components/HeroCarousel';
import CategorySection from '@/components/CategorySection';
import { CATEGORIAS } from '@/lib/categorias';

export default function Home() {
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
        {CATEGORIAS.map((cat) => (
          <CategorySection key={cat.slug} categoria={cat} />
        ))}
      </div>
    </main>
  );
}
