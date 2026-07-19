'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { supabase } from '@/lib/supabase-client';

export default function FavoritosPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session) {
        setLoading(false);
        return;
      }
      fetch('/api/favorites')
        .then((r) => r.json())
        .then((d) => setItems(d.items || []))
        .finally(() => setLoading(false));
    });
  }, []);

  const remove = async (id: string) => {
    await fetch(`/api/favorites?id=${id}`, { method: 'DELETE' });
    setItems((prev) => prev.filter((i) => i.id !== id));
  };

  if (loading) return <p className="p-6 text-gray-400">Cargando...</p>;

  return (
    <main className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">❤️ Mis Favoritos</h1>

      {items.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <p className="text-lg mb-2">No tenés favoritos aún</p>
          <Link href="/" className="text-blue-600 hover:underline text-sm">Explorar productos</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.id} className="flex items-center gap-4 border rounded-lg p-3 bg-white">
              {item.product_image && (
                <img src={item.product_image} alt="" className="w-16 h-16 object-contain rounded" />
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium line-clamp-1">{item.product_name}</p>
                <p className="text-xs text-gray-400">{item.store_origin}</p>
              </div>
              <button
                onClick={() => remove(item.id)}
                className="text-red-500 text-sm hover:underline shrink-0 cursor-pointer"
              >
                Quitar
              </button>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
