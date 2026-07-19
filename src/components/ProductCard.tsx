'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Product } from '@/lib/types';
import { supabase } from '@/lib/supabase';

export default function ProductCard({ product, showCategory }: { product: Product; showCategory?: boolean }) {
  const [isFav, setIsFav] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });
  }, []);

  useEffect(() => {
    if (!user || !product.external_id) return;
    fetch('/api/favorites')
      .then((r) => r.json())
      .then((d) => {
        const favs = d.items || [];
        setIsFav(favs.some((f: any) => f.product_external_id === product.external_id));
      })
      .catch(() => {});
  }, [user, product.external_id]);

  const toggleFav = async () => {
    if (!user) {
      await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: `${window.location.origin}/api/auth/callback` },
      });
      return;
    }
    if (isFav) {
      await fetch(`/api/favorites?product_external_id=${product.external_id}`, { method: 'DELETE' });
      setIsFav(false);
      window.dispatchEvent(new Event('fav-added'));
    } else {
      await fetch('/api/favorites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_external_id: product.external_id,
          product_name: product.name,
          product_image: product.image_url,
          product_price: product.price,
          store_origin: product.store_origin,
        }),
      });
      setIsFav(true);
      window.dispatchEvent(new Event('fav-added'));
    }
  };

  const addToCart = async () => {
    if (!user) {
      await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: `${window.location.origin}/api/auth/callback` },
      });
      return;
    }
      await fetch('/api/cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_external_id: product.external_id,
        product_name: product.name,
        product_image: product.image_url,
        product_price: product.price,
        store_origin: product.store_origin,
        source_url: product.source_url,
      }),
    });
    window.dispatchEvent(new Event('cart-added'));
  };

  const whatsappLink = product.whatsapp_message || (
    `https://wa.me/5959XXXXXXXX?text=${encodeURIComponent(
      `Hola! quisiera saber sobre "${product.name}" y su precio, muchas gracias :D`
    )}`
  );

  return (
    <div className="border rounded-lg p-3 flex flex-col bg-white relative">
      <button
        onClick={toggleFav}
        className={`absolute top-2 right-2 text-xl cursor-pointer z-10 ${isFav ? 'text-red-500' : 'text-gray-300 hover:text-red-400'}`}
        title={isFav ? 'Quitar de favoritos' : 'Agregar a favoritos'}
      >
        {isFav ? '♥' : '♡'}
      </button>

      <Link href={`/producto/${product.external_id}`} className="block">
        {product.image_url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={product.image_url} alt={product.name} className="w-full h-32 object-contain" />
        )}
        <h3 className="text-sm font-medium mt-2 line-clamp-2 hover:text-blue-700 transition-colors">{product.name}</h3>
      </Link>

      {(product as any).category && showCategory && (
        <span className="text-[10px] uppercase tracking-wide text-gray-400 mt-1">
          {(product as any).category}
        </span>
      )}

      <div className="flex gap-2 mt-3">
        <a
          href={whatsappLink}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 text-center bg-green-600 hover:bg-green-700 text-white text-sm font-semibold rounded-lg py-2.5 transition-colors"
        >
          WhatsApp
        </a>
        <button
          onClick={addToCart}
          className="px-3 py-2.5 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 cursor-pointer"
          title="Agregar al carrito"
        >
          🛒
        </button>
      </div>
    </div>
  );
}
