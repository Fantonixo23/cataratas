'use client';

import { useMemo, useState } from 'react';
import Fuse from 'fuse.js';
import ProductCard from '@/components/ProductCard';
import { Product } from '@/lib/types';

export default function SearchResults({ query, products }: { query: string; products: Product[] }) {
  const [currentPage, setCurrentPage] = useState(1);
  const perPage = 50;

  const fuse = useMemo(
    () =>
      new Fuse(products, {
        keys: ['name'],
        threshold: 0.4,
        distance: 100,
        minMatchCharLength: 2,
      }),
    [products]
  );

  const results = useMemo(() => {
    const q = query.trim();
    if (!q || q.length < 2) return products;
    return fuse.search(q).map((r) => r.item);
  }, [query, fuse, products]);

  const totalPages = Math.ceil(results.length / perPage);
  const pageResults = results.slice(0, currentPage * perPage);

  return (
    <>
      <p className="text-sm text-gray-400 mb-4">
        {results.length} resultado{results.length !== 1 ? 's' : ''}
      </p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {pageResults.map((p) => (
          <ProductCard key={p.external_id || p.name} product={p} showCategory />
        ))}
      </div>

      {results.length === 0 && query.trim().length >= 2 && (
        <p className="text-gray-400 mt-8 text-center">
          No se encontraron productos para &ldquo;{query}&rdquo;
        </p>
      )}

      {results.length === 0 && query.trim().length < 2 && (
        <p className="text-gray-400 mt-8 text-center">
          Escribí al menos 2 caracteres para buscar
        </p>
      )}

      {currentPage < totalPages && (
        <div className="text-center mt-8">
          <button
            onClick={() => setCurrentPage((p) => p + 1)}
            className="px-6 py-2.5 bg-blue-900 text-white rounded-lg hover:bg-blue-800 cursor-pointer text-sm"
          >
            Mostrar más ({results.length - currentPage * perPage} restantes)
          </button>
        </div>
      )}
    </>
  );
}
