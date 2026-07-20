'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Product } from '@/lib/types';

export default function HeroCarousel({ products }: { products: Product[] }) {
  const items = products.filter((p) => p.image_url).slice(0, 8);
  const [current, setCurrent] = useState(0);

  const next = useCallback(() => setCurrent((c) => (c + 1) % items.length), [items.length]);
  const prev = useCallback(() => setCurrent((c) => (c - 1 + items.length) % items.length), [items.length]);

  useEffect(() => {
    if (items.length < 2) return;
    const t = setInterval(next, 4000);
    return () => clearInterval(t);
  }, [next, items.length]);

  if (items.length === 0) return null;

  const p = items[current];

  return (
    <div className="relative w-full overflow-hidden rounded-xl bg-gray-100" style={{ aspectRatio: '16/7' }}>
      <Link href={`/buscar?q=${encodeURIComponent((p.name || '').split(' ').slice(0, 3).join(' '))}`}>
        <img
          src={p.image_url!}
          alt={p.name}
          className="absolute inset-0 w-full h-full object-contain p-4"
        />
      </Link>

      <button
        onClick={prev}
        className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/60 text-white rounded-full w-10 h-10 flex items-center justify-center cursor-pointer text-xl z-10"
      >
        ‹
      </button>
      <button
        onClick={next}
        className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/60 text-white rounded-full w-10 h-10 flex items-center justify-center cursor-pointer text-xl z-10"
      >
        ›
      </button>

      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-2 z-10">
        {items.map((_, i) => (
          <button
            key={i}
            onClick={() => setCurrent(i)}
            className={`w-2.5 h-2.5 rounded-full cursor-pointer transition-colors ${
              i === current ? 'bg-white' : 'bg-white/50'
            }`}
          />
        ))}
      </div>
    </div>
  );
}
