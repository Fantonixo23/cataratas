'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { CATEGORIAS } from '@/lib/categorias';
import { useSidebar } from '@/lib/sidebar-context';

export default function Sidebar() {
  const pathname = usePathname();
  const { open, close } = useSidebar();

  return (
    <>
      {/* Backdrop (mobile only) */}
      {open && (
        <div
          className="fixed inset-0 bg-black/40 z-40 lg:hidden"
          onClick={close}
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={`
          fixed top-0 left-0 z-50 h-full w-72 bg-white
          border-r shadow-xl
          transition-transform duration-300 ease-in-out
          -translate-x-full
          ${open ? 'translate-x-0' : ''}
          lg:!translate-x-0 lg:!static lg:!z-auto lg:!shadow-none
          lg:sticky lg:top-0 lg:h-screen lg:w-72 lg:shrink-0 lg:border-r lg:overflow-y-auto
        `}
      >
        <div className="p-4">
          {/* Close button (mobile only) */}
          <button
            onClick={close}
            className="lg:hidden ml-auto block mb-2 text-gray-500 hover:text-gray-800"
            aria-label="Cerrar menú"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
              <path fillRule="evenodd" d="M5.47 5.47a.75.75 0 011.06 0L12 10.94l5.47-5.47a.75.75 0 111.06 1.06L13.06 12l5.47 5.47a.75.75 0 11-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 01-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 010-1.06z" clipRule="evenodd" />
            </svg>
          </button>

          <div className="text-lg font-bold mb-3 text-blue-900">Categorías</div>
          <nav className="space-y-0.5">
            {CATEGORIAS.map((cat) => {
              const active = pathname === `/categoria/${cat.slug}`;
              return (
                <Link
                  key={cat.slug}
                  href={`/categoria/${cat.slug}`}
                  onClick={close}
                  className={`
                    flex items-center gap-3 px-3 py-2.5 text-sm transition-colors
                    border-l-4
                    ${active
                      ? 'bg-blue-600 text-white border-l-4 border-blue-800 font-medium'
                      : 'text-gray-700 hover:bg-blue-50 border-l-4 border-transparent hover:border-blue-300'
                    }
                  `}
                >
                  <span className="text-lg">{cat.icon}</span>
                  <span>{cat.name}</span>
                </Link>
              );
            })}
          </nav>

          <div className="mt-5">
            <Link
              href="/buscar"
              onClick={close}
              className={`
                flex items-center gap-3 px-3 py-2.5 text-sm transition-colors
                border-l-4 border-transparent text-gray-700 hover:text-blue-600 hover:border-blue-300
              `}
            >
              <span className="text-lg">🔍</span>
              <span>Buscar todos</span>
            </Link>
          </div>
        </div>
      </aside>
    </>
  );
}
