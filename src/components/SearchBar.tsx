'use client';

import { useEffect, useState, useMemo, useCallback } from 'react';
import Fuse from 'fuse.js';
import ProductCard from './ProductCard';
import { Product } from '@/lib/types';

export default function SearchBar() {
  const [query, setQuery] = useState('');
  const [allProducts, setAllProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/scrape')
      .then((r) => r.json())
      .then((d) => setAllProducts(d.products || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const fuse = useMemo(
    () =>
      new Fuse(allProducts, {
        keys: ['name'],
        threshold: 0.4,
        distance: 100,
        minMatchCharLength: 2,
      }),
    [allProducts]
  );

  const results = useMemo(() => {
    const q = query.trim();
    if (!q || q.length < 2) return allProducts;
    return fuse.search(q).map((r) => r.item);
  }, [query, fuse, allProducts]);

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Buscar iPhone, Samsung, notebook..."
        className="w-full p-3 border rounded-lg text-base"
      />

      {loading && <p className="text-sm text-gray-400 mt-2">Cargando productos...</p>}

      {!loading && allProducts.length === 0 && (
        <p className="text-sm text-gray-400 mt-2">
          No hay productos. Ejecutá <code>python main.py</code> en scraper-py/
        </p>
      )}

      {query.trim().length >= 2 && (
        <p className="text-xs text-gray-400 mt-2">
          {results.length} resultado{results.length !== 1 ? 's' : ''} para &ldquo;{query}&rdquo;
        </p>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
        {results.map((p, i) => (
          <ProductCard key={p.external_id || i} product={p} />
        ))}
      </div>
    </div>
  );
}
