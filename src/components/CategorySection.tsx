'use client';

import { useEffect, useState } from 'react';
import ProductCard from './ProductCard';
import Link from 'next/link';
import { Categoria } from '@/lib/categorias';

interface Product {
  name: string;
  price: number | null;
  image_url: string | null;
  source_url: string;
  store_origin: string;
  external_id: string;
  category: string;
}

interface Props {
  categoria: Categoria;
}

export default function CategorySection({ categoria }: Props) {
  const [products, setProducts] = useState<Product[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(true);
  const limit = 20;

  useEffect(() => {
    setLoading(true);
    fetch(`/api/products?category=${encodeURIComponent(categoria.name)}&page=${page}&limit=${limit}`)
      .then((r) => r.json())
      .then((data) => {
        setProducts(data.products || []);
        setTotalPages(data.totalPages || 0);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [page, categoria.name]);

  if (!loading && products.length === 0) return null;

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">
          {categoria.icon} {categoria.name}
        </h2>
        <Link href={`/categoria/${categoria.slug}`} className="text-sm text-blue-600 hover:underline">
          Ver todos
        </Link>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {products.map((p) => (
          <ProductCard key={p.external_id || p.external_id} product={p} />
        ))}
      </div>

      {loading && (
        <div className="text-center py-4 text-gray-400 text-sm">Cargando...</div>
      )}

      {totalPages > 1 && !loading && (
        <div className="flex items-center justify-center gap-4 mt-6">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
            className="px-4 py-2 text-sm rounded-lg bg-gray-100 hover:bg-gray-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            ← Anterior
          </button>
          <span className="text-sm text-gray-500">
            Página {page} de {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="px-4 py-2 text-sm rounded-lg bg-gray-100 hover:bg-gray-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            Siguiente →
          </button>
        </div>
      )}
    </section>
  );
}
