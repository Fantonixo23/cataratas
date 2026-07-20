'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { CATEGORIAS } from '@/lib/categorias';

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-80 shrink-0 border-l bg-white p-4 overflow-y-auto sticky top-0 h-screen">
      <div className="text-lg font-bold mb-4 px-3 text-blue-900">Categorías</div>
      <nav className="space-y-1">
        {CATEGORIAS.map((cat) => {
          const active = pathname === `/categoria/${cat.slug}`;
          return (
            <Link
              key={cat.slug}
              href={`/categoria/${cat.slug}`}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                active
                  ? 'bg-blue-900 text-white font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <span className="text-lg">{cat.icon}</span>
              <span>{cat.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-6 px-3">
        <Link
          href="/buscar"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-700 hover:bg-gray-100 transition-colors"
        >
          <span className="text-lg">🔍</span>
          <span>Buscar todos</span>
        </Link>
      </div>
    </aside>
  );
}
