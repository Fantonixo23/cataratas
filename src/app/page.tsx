import SearchBar from '@/components/SearchBar';

export default function Home() {
  return (
    <main className="max-w-5xl mx-auto p-6">
      <header className="mb-6">
        <h1 className="text-3xl font-bold">Catarata</h1>
        <p className="text-gray-500 mt-1">Buscá productos y consultá precios por WhatsApp</p>
      </header>

      <SearchBar />

      <footer className="mt-12 pb-8">
        <p className="text-xs text-gray-400 text-center">
          Los resultados de búsqueda provienen del buscador de MercadoLibre Argentina.
          Catarata no es una tienda ni garantiza disponibilidad o precio final; para
          cerrar tu compra te contactamos por WhatsApp.
        </p>
      </footer>
    </main>
  );
}
