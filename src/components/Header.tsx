'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { supabase } from '@/lib/supabase-client';

interface Suggestion {
  name: string;
  external_id: string;
  image_url: string | null;
  price: number | null;
  store_origin: string;
}

export default function Header() {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [favCount, setFavCount] = useState(0);
  const [cartCount, setCartCount] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLFormElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

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
    if (!user) { setFavCount(0); setCartCount(0); return; }
    const load = () => {
      fetch('/api/favorites').then(r => r.json()).then(d => setFavCount(d.items?.length ?? 0)).catch(() => {});
      fetch('/api/cart').then(r => r.json()).then(d => setCartCount(d.items?.length ?? 0)).catch(() => {});
    };
    load();
    const onCart = () => { setCartCount(c => c + 1); };
    const onFav = () => { setFavCount(c => c + 1); };
    window.addEventListener('cart-added', onCart);
    window.addEventListener('fav-added', onFav);
    window.addEventListener('focus', load);
    return () => {
      window.removeEventListener('cart-added', onCart);
      window.removeEventListener('fav-added', onFav);
      window.removeEventListener('focus', load);
    };
  }, [user]);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (query.trim().length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    debounceRef.current = setTimeout(() => {
      fetch(`/api/products/search?q=${encodeURIComponent(query.trim())}&limit=6`)
        .then(r => r.json())
        .then(data => {
          setSuggestions(data.products || []);
          setShowSuggestions(data.products?.length > 0);
        })
        .catch(() => {});
    }, 300);
  }, [query]);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node) &&
          inputRef.current && !inputRef.current.contains(e.target as Node)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleLogin = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: `${window.location.origin}/api/auth/callback` },
    });
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
  };

  return (
    <header className="bg-blue-900 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-4">
        <Link href="/" className="text-xl font-bold tracking-tight shrink-0">
          Catarata
        </Link>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (query.trim().length >= 2) {
              window.location.href = `/buscar?q=${encodeURIComponent(query.trim())}`;
            }
          }}
          className="relative flex-1 max-w-lg"
          ref={dropdownRef}
        >
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => { if (suggestions.length > 0) setShowSuggestions(true); }}
            placeholder="Buscar iPhone, Samsung, notebook..."
            className="w-full px-4 py-2 rounded-lg bg-white text-gray-800 text-sm border border-gray-300 outline-none focus:ring-2 focus:ring-blue-400"
          />

          {showSuggestions && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-xl border border-gray-200 z-50 overflow-hidden">
              {suggestions.map((p) => (
                <Link
                  key={p.external_id}
                  href={`/producto/${p.external_id}`}
                  onClick={() => setShowSuggestions(false)}
                  className="flex items-center gap-3 px-4 py-2 hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0"
                >
                  {p.image_url ? (
                    <img src={p.image_url} alt="" className="w-10 h-10 object-contain rounded" />
                  ) : (
                    <div className="w-10 h-10 bg-gray-100 rounded" />
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-800 truncate">{p.name}</p>
                    <p className="text-xs text-gray-400 uppercase">{p.store_origin}</p>
                  </div>
                  {p.price && (
                    <span className="text-sm text-gray-600 font-medium whitespace-nowrap">
                      Gs. {p.price.toLocaleString('es-PY')}
                    </span>
                  )}
                </Link>
              ))}
              <Link
                href={`/buscar?q=${encodeURIComponent(query.trim())}`}
                onClick={() => setShowSuggestions(false)}
                className="block px-4 py-2 text-center text-sm text-blue-600 hover:bg-blue-50 font-medium"
              >
                Ver todos los resultados →
              </Link>
            </div>
          )}
        </form>

        <div className="flex items-center gap-3">
          <Link href="/favoritos" className="relative text-xl hover:opacity-80" title="Favoritos">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
              <path d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z" />
            </svg>
            {favCount > 0 && (
              <span className="absolute -top-1.5 -right-1.5 bg-red-600 text-white text-[10px] font-bold rounded-full min-w-[16px] h-4 flex items-center justify-center px-1 leading-none">
                {favCount}
              </span>
            )}
          </Link>

          <Link href="/carrito" className="relative text-xl hover:opacity-80" title="Carrito">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
              <path d="M2.25 2.25a.75.75 0 000 1.5h1.386c.17 0 .318.114.362.278l2.558 9.592a3.752 3.752 0 00-2.806 3.63c0 .414.336.75.75.75h15.75a.75.75 0 000-1.5H5.378A2.25 2.25 0 017.5 15h11.218a.75.75 0 00.674-.421 60.358 60.358 0 002.96-7.228.75.75 0 00-.525-.96A60.864 60.864 0 005.68 4.509l-.232-.867A1.875 1.875 0 003.636 2.25H2.25zM3.75 20.25a1.5 1.5 0 113 0 1.5 1.5 0 01-3 0zM16.5 20.25a1.5 1.5 0 113 0 1.5 1.5 0 01-3 0z" />
            </svg>
            {cartCount > 0 && (
              <span className="absolute -top-1.5 -right-1.5 bg-red-600 text-white text-[10px] font-bold rounded-full min-w-[16px] h-4 flex items-center justify-center px-1 leading-none">
                {cartCount}
              </span>
            )}
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
  );
}
