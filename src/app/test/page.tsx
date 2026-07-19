'use client';

import { useEffect, useState } from 'react';

interface Product {
  name: string;
  price: string;
  image_url: string;
  source_url: string;
  store_origin: string;
}

export default function TestPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch('/api/scrape');
        const data = await res.json();
        if (!res.ok) throw new Error(data.error);
        setProducts(data.products);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div className="p-8 text-center text-gray-400">Cargando...</div>;

  if (error) return (
    <div className="p-8 text-center">
      <p className="text-red-500">{error}</p>
      <p className="text-gray-400 mt-2">Ejecutá <code className="bg-gray-100 px-2 py-1 rounded">python main.py</code> en la carpeta <code>scraper-py/</code></p>
    </div>
  );

  return (
    <main className="max-w-5xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-1">Catarata — Test de scraping</h1>
      <p className="text-gray-400 text-sm mb-6">{products.length} productos scrapeados</p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {products.map((p, i) => (
          <div key={i} className="border rounded-lg p-3 flex flex-col">
            {p.image_url && (
              <img src={p.image_url} alt={p.name} className="w-full h-32 object-contain" />
            )}
            <h3 className="text-sm font-medium mt-2 line-clamp-2">{p.name}</h3>
            <p className="text-xs text-gray-400 mt-1">${p.price} Gs.</p>
            <p className="text-xs text-gray-400">{p.store_origin}</p>
            <a
              href={`https://wa.me/5959XXXXXXXX?text=${encodeURIComponent(`Hola! quisiera saber sobre "${p.name}" y su precio, muchas gracias :D`)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="block text-center bg-green-600 hover:bg-green-700 text-white text-sm font-semibold rounded-lg py-2 mt-3 transition-colors"
            >
              Consultar por WhatsApp
            </a>
          </div>
        ))}
      </div>
    </main>
  );
}
