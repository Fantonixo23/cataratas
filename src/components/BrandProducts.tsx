'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import ProductCard from '@/components/ProductCard';
import { Product } from '@/lib/types';

const LIMIT = 24;

export default function BrandProducts({ slug }: { slug: string }) {
  const [products, setProducts] = useState<Product[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [brandName, setBrandName] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setPage(1);
  }, [slug]);

  useEffect(() => {
    let cancelled = false;
    fetch(`/api/products?brand=${encodeURIComponent(slug)}&page=${page}&limit=${LIMIT}`)
      .then((r) => r.json())
      .then((d) => {
        if (cancelled) return;
        setProducts(d.products || []);
        setTotalPages(d.totalPages || 0);
        setTotal(d.total || 0);
        setBrandName(d.products?.[0]?.brand || null);
        setLoading(false);
      })
      .catch(() => !cancelled && setLoading(false));
    return () => { cancelled = true; };
  }, [slug, page]);

  // El titulo legible sale del primer producto de la pagina; si estamos en una
  // pagina vacia al final, conservamos el que ya teniamos.
  const heading = brandName || slug.replace(/-/g, ' ');

  return (
    <section className="py-6 space-y-6">
      <nav className="text-xs text-gray-500 flex items-center gap-1.5">
        <Link href="/" className="hover:underline">Inicio</Link>
        <span aria-hidden>/</span>
        <Link href="/marcas" className="hover:underline">Marcas</Link>
        <span aria-hidden>/</span>
        <span className="text-gray-700">{heading}</span>
      </nav>

      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h1 className="text-2xl font-bold capitalize">{heading}</h1>
        {!loading && total > 0 && (
          <span className="text-sm text-gray-500">
            {total} {total === 1 ? 'producto' : 'productos'}
          </span>
        )}
      </div>

      {!loading && products.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <p className="mb-3">No encontramos productos para esta marca.</p>
          <Link href="/marcas" className="text-blue-600 hover:underline">Ver todas las marcas</Link>
        </div>
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

      {loading && <p className="text-center text-gray-400 text-sm">Cargando...</p>}

      {totalPages > 1 && !loading && (
        <div className="flex items-center justify-center gap-4 mt-6">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
            className="px-4 py-2 text-sm rounded-lg bg-white border border-gray-200 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            ← Anterior
          </button>
          <span className="text-sm text-gray-500">Página {page} de {totalPages}</span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="px-4 py-2 text-sm rounded-lg bg-white border border-gray-200 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            Siguiente →
          </button>
        </div>
      )}
    </section>
  );
}
