'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { IMAGES } from '@/lib/images';

interface Brand {
  brand: string;
  slug: string;
  products: number;
}

const MIN_PRODUCTS = 3;

export default function MarcasPage() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [effectiveMin, setEffectiveMin] = useState(MIN_PRODUCTS);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [imgOk, setImgOk] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setEffectiveMin(MIN_PRODUCTS);

    const load = (m: number) =>
      fetch(`/api/brands?min=${m}&limit=500`)
        .then((r) => r.json())
        .then((d) => (d.brands || []) as Brand[]);

    load(MIN_PRODUCTS)
      .then((rows) => {
        if (cancelled) return;
        if (rows.length > 0) {
          setBrands(rows);
          return;
        }
        // Catalogo chico: sin marcas con 3+ productos no hay nada que listar,
        // asi que bajamos el corte a 1 antes de mostrar la pagina vacia.
        return load(1).then((fallback) => {
          if (cancelled) return;
          setEffectiveMin(1);
          setBrands(fallback);
        });
      })
      .catch(() => {})
      .finally(() => !cancelled && setLoading(false));

    return () => { cancelled = true; };
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return brands;
    return brands.filter((b) => b.brand.toLowerCase().includes(q));
  }, [brands, query]);

  return (
    <section className="py-6 space-y-6">
      <div
        className="relative overflow-hidden rounded-2xl"
        style={{ background: 'linear-gradient(120deg, #0b2a6b 0%, #123f9e 100%)' }}
      >
        {imgOk && (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={IMAGES.franjaComercio}
            alt=""
            onError={() => setImgOk(false)}
            className="absolute inset-0 h-full w-full object-cover opacity-35"
          />
        )}
        <div className="relative px-6 py-10 text-white">
          <h1 className="text-2xl md:text-3xl font-bold">Marcas</h1>
          <p className="text-sm text-blue-100 mt-1 max-w-2xl">
            {effectiveMin === MIN_PRODUCTS ? (
              <>Mostramos las marcas que tienen al menos {MIN_PRODUCTS} productos en el catálogo.</>
            ) : (
              <>
                El catálogo todavía es chico, así que mostramos las marcas con{' '}
                {effectiveMin} producto. Cuando se carguen más productos vamos a exigir al menos{' '}
                {MIN_PRODUCTS}.
              </>
            )}{' '}
            Si buscás una marca puntual y no aparece, probá con el buscador de arriba.
          </p>
        </div>
      </div>

      {brands.length > 12 && (
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Filtrar marcas..."
          className="w-full max-w-sm px-4 py-2.5 rounded-lg border border-gray-300 text-sm outline-none focus:ring-2 focus:ring-blue-400"
        />
      )}

      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3" aria-hidden>
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="h-20 animate-pulse rounded-xl bg-white" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <p className="text-gray-400 text-sm">
          {brands.length === 0
            ? 'Todavía no hay marcas con suficientes productos en el catálogo.'
            : 'Ninguna marca coincide con ese filtro.'}
        </p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {filtered.map((b) => (
            <Link
              key={b.slug}
              href={`/marca/${b.slug}`}
              className="group flex flex-col items-center justify-center gap-1 rounded-xl border border-gray-200 bg-white px-4 py-5 text-center hover:border-blue-300 hover:shadow-md transition-all"
            >
              <span className="font-semibold text-gray-800 group-hover:text-blue-700">
                {b.brand}
              </span>
              <span className="text-[11px] text-gray-400">
                {b.products} {b.products === 1 ? 'producto' : 'productos'}
              </span>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
