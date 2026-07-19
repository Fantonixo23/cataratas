'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { supabase } from '@/lib/supabase-client';
import { getCategoriaByName } from '@/lib/categorias';
import { getStoreInfo } from '@/lib/stores';
import { Product } from '@/lib/types';

export default function ProductoPage() {
  const { id } = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [cantidad, setCantidad] = useState(1);
  const [user, setUser] = useState<any>(null);
  const [addedMsg, setAddedMsg] = useState('');

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });
  }, []);

  useEffect(() => {
    if (!id) return;
    fetch(`/api/product/${id}`)
      .then((r) => r.json())
      .then((d) => {
        if (d.product) setProduct(d.product);
        else setProduct(null);
      })
      .finally(() => setLoading(false));
  }, [id]);

  const addToCart = async () => {
    if (!user) {
      await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: `${window.location.origin}/api/auth/callback` },
      });
      return;
    }
    if (!product) return;

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
    setAddedMsg('✓ Agregado al carrito');
    setTimeout(() => setAddedMsg(''), 3000);
  };

  if (loading) return <p className="p-6 text-gray-400">Cargando producto...</p>;

  if (!product) return (
    <main className="max-w-3xl mx-auto p-6 text-center">
      <p className="text-gray-400 mb-4">Producto no encontrado</p>
      <Link href="/" className="text-blue-600 hover:underline">Volver al inicio</Link>
    </main>
  );

  return (
    <main className="max-w-3xl mx-auto p-4 md:p-6">
      <nav className="text-sm text-gray-400 mb-4">
        <Link href="/" className="hover:text-gray-600">Inicio</Link>
        {(() => {
          const cat = product.category ? getCategoriaByName(product.category) : null;
          return cat ? (
            <>
              <span className="mx-2">/</span>
              <Link href={`/categoria/${cat.slug}`} className="hover:text-gray-600">{cat.name}</Link>
            </>
          ) : null;
        })()}
        <span className="mx-2">/</span>
        <span className="text-gray-800">{product.name}</span>
      </nav>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg p-4 border flex items-center justify-center">
          {product.image_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={product.image_url} alt={product.name} className="max-h-80 object-contain" />
          )}
        </div>

        <div>
          <h1 className="text-xl md:text-2xl font-bold mb-2">{product.name}</h1>

          <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
            <span className="bg-gray-100 px-2 py-0.5 rounded text-xs font-mono">
              SKU#: {product.external_id}
            </span>
          </div>

          <p className="text-sm text-gray-500 mb-4 italic">
            Consulte disponibilidad
          </p>

          <div className="flex items-center gap-3 mb-4">
            <span className="text-sm font-medium text-gray-600">Cantidad:</span>
            <div className="flex items-center border rounded-lg">
              <button
                onClick={() => setCantidad(Math.max(1, cantidad - 1))}
                className="px-3 py-1.5 text-lg hover:bg-gray-50 cursor-pointer"
              >
                −
              </button>
              <span className="px-4 py-1.5 text-sm font-medium border-x min-w-[3rem] text-center">
                {cantidad}
              </span>
              <button
                onClick={() => setCantidad(cantidad + 1)}
                className="px-3 py-1.5 text-lg hover:bg-gray-50 cursor-pointer"
              >
                +
              </button>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={addToCart}
              className="flex-1 bg-blue-900 text-white font-semibold py-3 rounded-lg hover:bg-blue-800 transition-colors cursor-pointer"
            >
              Agregar al carrito
            </button>
            <a
              href={`https://wa.me/5959XXXXXXXX?text=${encodeURIComponent(`Hola! quisiera saber sobre "${product.name}" (SKU: ${product.external_id}) y su precio, muchas gracias :D`)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 transition-colors text-sm font-semibold shrink-0"
            >
              WhatsApp
            </a>
          </div>

          {addedMsg && (
            <p className="mt-2 text-sm text-green-600 font-medium">{addedMsg}</p>
          )}
        </div>
      </div>

      <section className="mt-8 border rounded-lg p-4 bg-white">
        <h2 className="text-lg font-semibold mb-3">Detalles</h2>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between border-b pb-1.5">
            <span className="text-gray-500">SKU</span>
            <span className="font-mono">{product.external_id}</span>
          </div>
          {(() => {
            const store = getStoreInfo(product.store_origin);
            return (
              <>
                <div className="flex justify-between border-b pb-1.5">
                  <span className="text-gray-500">Tienda</span>
                  <span>{store?.name ?? product.store_origin}</span>
                </div>
                <div className="flex justify-between border-b pb-1.5">
                  <span className="text-gray-500">Procedencia</span>
                  <span>{store?.location ?? "Ciudad del Este, Paraguay"}</span>
                </div>
              </>
            );
          })()}
          {product.category && (
            <div className="flex justify-between border-b pb-1.5">
              <span className="text-gray-500">Categoría</span>
              <span>{product.category}</span>
            </div>
          )}
          <a
            href={product.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="block text-blue-600 hover:underline pt-1"
          >
            Ver producto original →
          </a>
        </div>
      </section>

      <section className="mt-4 border rounded-lg p-4 bg-white">
        <h2 className="text-lg font-semibold mb-2">Más información</h2>
        <p className="text-sm text-gray-500">
          Para consultar precio, disponibilidad y realizar tu compra, comunicate con nosotros
          a través del botón de WhatsApp. Te responderemos a la brevedad.
        </p>
        <p className="text-sm text-gray-500 mt-2">
          También podés agregar este producto a tu carrito y consultar por todos los
          productos juntos desde la sección <Link href="/carrito" className="text-blue-600 hover:underline">Carrito</Link>.
        </p>
      </section>
    </main>
  );
}
