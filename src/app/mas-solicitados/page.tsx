'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import ProductCard from '@/components/ProductCard';
import { Product } from '@/lib/types';

export default function MasSolicitadosPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [isTrending, setIsTrending] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetch('/api/products/trending?limit=48&days=30')
      .then((r) => r.json())
      .then((d) => {
        if (cancelled) return;
        setProducts(d.products || []);
        setIsTrending(!!d.trending);
      })
      .catch(() => {})
      .finally(() => !cancelled && setLoading(false));
    return () => { cancelled = true; };
  }, []);

  return (
    <section className="py-6 space-y-4">
      <nav className="text-xs text-gray-500 flex items-center gap-1.5">
        <Link href="/" className="hover:underline">Inicio</Link>
        <span aria-hidden>/</span>
        <span className="text-gray-700">Más solicitados</span>
      </nav>

      <div>
        <h1 className="text-2xl font-bold">🔥 Más solicitados</h1>
        <p className="text-sm text-gray-500 mt-1 max-w-2xl">
          {isTrending
            ? 'Ordenados por la interacción real de los clientes, con los clics de la última semana valiendo el doble que los de hace dos semanas.'
            : 'Todavía no hay datos de interacción. Cuando los clientes empiecen a navegar, el orden se arma solo.'}
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4" aria-hidden>
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-56 animate-pulse rounded-lg bg-white" />
          ))}
        </div>
      ) : products.length === 0 ? (
        <p className="text-gray-400 text-sm">Todavía no hay productos para mostrar.</p>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {products.map((p) => (
            <ProductCard
              key={`${p.store_origin}-${p.external_id}`}
              product={p}
              showCategory
            />
          ))}
        </div>
      )}
    </section>
  );
}
