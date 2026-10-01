'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Brand {
  brand: string;
  slug: string;
  products: number;
}

export default function BrandsStrip({
  limit = 18,
  min = 3,
  title = 'Marcas',
  subtitle,
}: {
  limit?: number;
  min?: number;
  title?: string;
  subtitle?: string;
}) {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [effectiveMin, setEffectiveMin] = useState(min);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setEffectiveMin(min);

    const load = (m: number) =>
      fetch(`/api/brands?min=${m}&limit=${limit}`)
        .then((r) => r.json())
        .then((d) => (d.brands || []) as Brand[]);

    // El corte de "min" existe para no llenar la grilla de marcas de un solo
    // producto. Si el catalogo es chico todavia y no queda ninguna, relajamos
    // a 1 en vez de mostrar una seccion vacia.
    load(min)
      .then((rows) => {
        if (cancelled) return;
        if (rows.length > 0 || min === 1) {
          setBrands(rows);
          return;
        }
        return load(1).then((fallback) => {
          if (cancelled) return;
          setEffectiveMin(1);
          setBrands(fallback);
        });
      })
      .catch(() => {})
      .finally(() => !cancelled && setLoading(false));

    return () => { cancelled = true; };
  }, [min, limit]);

  if (loading) {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3" aria-hidden>
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-16 animate-pulse rounded-xl bg-white" />
        ))}
      </div>
    );
  }

  if (brands.length === 0) return null;

  return (
    <section>
      <div className="flex items-end justify-between gap-4 mb-4">
        <div>
          <h2 className="text-xl font-bold">{title}</h2>
          <p className="text-sm text-gray-500">
            {subtitle || 'Entrá por marca y encontrá todo lo que tenés de esa marca.'}
            {effectiveMin < min && (
              <span className="ml-1 text-xs text-amber-600">
                (pocas marcas con 3+ productos: mostramos todas)
              </span>
            )}
          </p>
        </div>
        <Link href="/marcas" className="text-sm font-medium text-blue-600 hover:underline shrink-0">
          Ver todas →
        </Link>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
        {brands.map((b) => (
          <Link
            key={b.slug}
            href={`/marca/${b.slug}`}
            className="group flex flex-col items-center justify-center gap-1 rounded-xl border border-gray-200 bg-white px-3 py-4 text-center hover:border-blue-300 hover:shadow-md transition-all"
          >
            <span className="text-sm font-semibold text-gray-800 group-hover:text-blue-700 line-clamp-2">
              {b.brand}
            </span>
            <span className="text-[11px] text-gray-400">
              {b.products} {b.products === 1 ? 'producto' : 'productos'}
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}
