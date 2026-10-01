'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import ProductCard from '@/components/ProductCard';
import { Product } from '@/lib/types';

const AUTO_ADVANCE_MS = 6000;

export default function TrendingCarousel() {
  const [products, setProducts] = useState<Product[]>([]);
  const [isTrending, setIsTrending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [page, setPage] = useState(0);
  const [atStart, setAtStart] = useState(true);
  const [atEnd, setAtEnd] = useState(false);
  const [paused, setPaused] = useState(false);

  const trackRef = useRef<HTMLDivElement>(null);
  const touchRef = useRef<{ x: number; moved: boolean }>({ x: 0, moved: false });

  useEffect(() => {
    let cancelled = false;
    fetch('/api/products/trending?limit=16')
      .then((r) => r.json())
      .then((d) => {
        if (cancelled) return;
        if (d.error) {
          setFailed(true);
          return;
        }
        setProducts(d.products || []);
        setIsTrending(!!d.trending);
      })
      .catch(() => !cancelled && setFailed(true))
      .finally(() => !cancelled && setLoading(false));
    return () => { cancelled = true; };
  }, []);

  const updateEdges = useCallback(() => {
    const el = trackRef.current;
    if (!el) return;
    setAtStart(el.scrollLeft <= 4);
    setAtEnd(el.scrollLeft + el.clientWidth >= el.scrollWidth - 4);
  }, []);

  const scrollByPage = useCallback((dir: 1 | -1) => {
    const el = trackRef.current;
    if (!el) return;
    const amount = Math.max(240, el.clientWidth * 0.8);
    el.scrollBy({ left: dir * amount, behavior: 'smooth' });
  }, []);

  // Avance automatico. Se pausa con hover, con el dedo sobre el carrusel y
  // apenas el usuario scrollea a mano, para no pelearle el control.
  useEffect(() => {
    if (paused || loading || products.length === 0) return;
    const id = setInterval(() => {
      const el = trackRef.current;
      if (!el) return;
      if (el.scrollLeft + el.clientWidth >= el.scrollWidth - 8) {
        el.scrollTo({ left: 0, behavior: 'smooth' });
      } else {
        el.scrollBy({ left: Math.max(240, el.clientWidth * 0.8), behavior: 'smooth' });
      }
    }, AUTO_ADVANCE_MS);
    return () => clearInterval(id);
  }, [paused, loading, products.length]);

  const onTouchStart = (e: React.TouchEvent) => {
    touchRef.current = { x: e.touches[0].clientX, moved: false };
    setPaused(true);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    if (Math.abs(e.touches[0].clientX - touchRef.current.x) > 8) touchRef.current.moved = true;
  };

  const goTo = (i: number) => {
    const el = trackRef.current;
    if (!el) return;
    const card = el.querySelector('[data-card]') as HTMLElement | null;
    const step = card ? card.offsetWidth + 16 : Math.max(240, el.clientWidth * 0.8);
    el.scrollTo({ left: i * step, behavior: 'smooth' });
  };

  const visibleCount = Math.max(1, Math.ceil((products.length || 4) / 4));

  if (loading) {
    return (
      <div className="h-40 animate-pulse rounded-xl bg-white" aria-hidden />
    );
  }

  if (failed || products.length === 0) return null;

  return (
    <section
      className="rounded-2xl border border-blue-100 bg-white p-4 shadow-sm"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      <div className="mb-4 flex items-center gap-3">
        <span className="text-2xl" aria-hidden>🔥</span>
        <div className="min-w-0 flex-1">
          <h2 className="text-lg font-bold leading-tight">
            {isTrending ? 'Los más solicitados' : 'Productos destacados'}
          </h2>
          <p className="text-xs text-gray-500">
            {isTrending
              ? 'Ordenados por la interacción real de los clientes: clics, favoritos y carritos.'
              : 'Todavía no hay datos de interacción. Estos son los últimos del catálogo.'}
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-1">
          <button
            onClick={() => scrollByPage(-1)}
            disabled={atStart}
            aria-label="Anterior"
            className="h-8 w-8 rounded-full border border-gray-200 text-gray-600 disabled:opacity-30 enabled:hover:bg-gray-50 flex items-center justify-center cursor-pointer enabled:cursor-pointer"
          >
            ‹
          </button>
          <button
            onClick={() => scrollByPage(1)}
            disabled={atEnd}
            aria-label="Siguiente"
            className="h-8 w-8 rounded-full border border-gray-200 text-gray-600 disabled:opacity-30 enabled:hover:bg-gray-50 flex items-center justify-center cursor-pointer enabled:cursor-pointer"
          >
            ›
          </button>
        </div>
      </div>

      <div
        ref={trackRef}
        onScroll={updateEdges}
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={() => { if (touchRef.current.moved) setPaused(false); }}
        className="flex gap-4 overflow-x-auto scroll-smooth snap-x snap-mandatory pb-2 -mx-1 px-1 [scrollbar-width:thin]"
      >
        {products.map((p) => (
          <div
            key={`${p.store_origin}-${p.external_id}`}
            data-card
            className="shrink-0 w-56 snap-start"
          >
            <ProductCard product={p} showCategory />
          </div>
        ))}
      </div>

      <div className="mt-3 flex items-center justify-center gap-2">
        {Array.from({ length: visibleCount }).map((_, i) => (
          <button
            key={i}
            onClick={() => goTo(i)}
            aria-label={`Ir al grupo ${i + 1}`}
            className="h-1.5 w-8 rounded-full bg-blue-200 hover:bg-blue-400 transition-colors cursor-pointer"
          />
        ))}
        <Link
          href="/mas-solicitados"
          className="ml-3 text-xs font-medium text-blue-600 hover:underline"
        >
          Ver todos →
        </Link>
      </div>
    </section>
  );
}
