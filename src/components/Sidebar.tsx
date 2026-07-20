'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { CATEGORIAS } from '@/lib/categorias';
import { useSidebar } from '@/lib/sidebar-context';

export default function Sidebar() {
  const pathname = usePathname();
  const { open, close } = useSidebar();

  return (
    <div
      className={`
        overflow-hidden transition-all duration-300 ease-in-out
        bg-white border-b shadow-md
        ${open ? 'overflow-y-auto' : ''}
      `}
      style={{ maxHeight: open ? '80vh' : '0' }}
    >
      <div className="max-w-7xl mx-auto p-4">
        <nav className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
          {CATEGORIAS.map((cat) => {
            const active = pathname === `/categoria/${cat.slug}`;
            return (
              <Link
                key={cat.slug}
                href={`/categoria/${cat.slug}`}
                onClick={close}
                className={`
                  flex items-center gap-2 px-3 py-2.5 text-sm transition-colors rounded
                  ${active
                    ? 'bg-blue-600 text-white font-medium'
                    : 'text-gray-700 hover:bg-blue-50 border border-gray-200'
                  }
                `}
              >
                <span className="text-lg shrink-0">{cat.icon}</span>
                <span className="truncate">{cat.name}</span>
              </Link>
            );
          })}
          <Link
            href="/buscar"
            onClick={close}
            className="flex items-center gap-2 px-3 py-2.5 text-sm transition-colors rounded text-gray-700 hover:bg-blue-50 border border-gray-200"
          >
            <span className="text-lg shrink-0">🔍</span>
            <span className="truncate">Buscar todos</span>
          </Link>
        </nav>
      </div>
    </div>
  );
}
