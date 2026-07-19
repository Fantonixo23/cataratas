'use client';

import { useEffect, useState, useMemo, useRef } from 'react';
import Fuse from 'fuse.js';
import Link from 'next/link';
import Sidebar from './Sidebar';
import { Product } from '@/lib/types';
import { supabase } from '@/lib/supabase';

export default function Header() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [allProducts, setAllProducts] = useState<Product[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [user, setUser] = useState<any>(null);
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch('/api/scrape')
      .then((r) => r.json())
      .then((d) => setAllProducts(d.products || []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });
    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
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
    if (!q || q.length < 2) return [];
    return fuse.search(q).slice(0, 8).map((r) => r.item);
  }, [query, fuse]);

  const handleLogin = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
        options: { redirectTo: `${window.location.origin}/auth/callback` },
    });
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
  };

  return (
    <>
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <header className="bg-blue-900 text-white shadow-md">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-2xl cursor-pointer hover:opacity-80"
            aria-label="Abrir menú"
          >
            ☰
          </button>

          <Link href="/" className="text-xl font-bold tracking-tight shrink-0">
            Catarata
          </Link>

          <div ref={searchRef} className="relative flex-1 max-w-lg">
            <input
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
              placeholder="Buscar iPhone, Samsung, notebook..."
              className="w-full px-4 py-2 rounded-lg bg-white text-gray-800 text-sm border border-gray-300 outline-none focus:ring-2 focus:ring-blue-400"
            />

            {showDropdown && results.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white text-black rounded-lg shadow-xl border overflow-hidden z-50">
                {results.map((p) => (
                  <Link
                    key={p.external_id || p.name}
                    href={`/producto/${p.external_id}`}
                    className="flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50 text-sm border-b last:border-0"
                  >
                    {p.image_url && (
                      <img src={p.image_url} alt="" className="w-8 h-8 object-contain rounded" />
                    )}
                    <span className="line-clamp-1">{p.name}</span>
                    <span className="text-xs text-gray-400 ml-auto shrink-0">{p.store_origin}</span>
                  </Link>
                ))}
              </div>
            )}
          </div>

          <div className="flex items-center gap-3">
            <Link href="/favoritos" className="text-xl hover:opacity-80" title="Favoritos">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                <path d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z" />
              </svg>
            </Link>

            <Link href="/carrito" className="text-xl hover:opacity-80" title="Carrito">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                <path d="M2.25 2.25a.75.75 0 000 1.5h1.386c.17 0 .318.114.362.278l2.558 9.592a3.752 3.752 0 00-2.806 3.63c0 .414.336.75.75.75h15.75a.75.75 0 000-1.5H5.378A2.25 2.25 0 017.5 15h11.218a.75.75 0 00.674-.421 60.358 60.358 0 002.96-7.228.75.75 0 00-.525-.96A60.864 60.864 0 005.68 4.509l-.232-.867A1.875 1.875 0 003.636 2.25H2.25zM3.75 20.25a1.5 1.5 0 113 0 1.5 1.5 0 01-3 0zM16.5 20.25a1.5 1.5 0 113 0 1.5 1.5 0 01-3 0z" />
              </svg>
            </Link>

            {user ? (
              <div className="flex items-center gap-2">
                <span className="text-sm hidden md:inline">{user.email?.split('@')[0]}</span>
                <button onClick={handleLogout} className="text-xl hover:opacity-80" title="Cerrar sesión">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                    <path fillRule="evenodd" d="M7.5 3.75A1.5 1.5 0 006 5.25v13.5a1.5 1.5 0 001.5 1.5h6a1.5 1.5 0 001.5-1.5V15a.75.75 0 011.5 0v3.75a3 3 0 01-3 3h-6a3 3 0 01-3-3V5.25a3 3 0 013-3h6a3 3 0 013 3V9A.75.75 0 0115 9V5.25a1.5 1.5 0 00-1.5-1.5h-6zm5.03 4.72a.75.75 0 010 1.06l-1.72 1.72h10.94a.75.75 0 010 1.5H10.81l1.72 1.72a.75.75 0 11-1.06 1.06l-3-3a.75.75 0 010-1.06l3-3a.75.75 0 011.06 0z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            ) : (
              <button onClick={handleLogin} className="text-xl hover:opacity-80" title="Iniciar sesión">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                  <path fillRule="evenodd" d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z" clipRule="evenodd" />
                </svg>
              </button>
            )}
          </div>
        </div>
      </header>
    </>
  );
}
