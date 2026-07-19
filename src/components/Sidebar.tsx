'use client';

import { useState } from 'react';
import Link from 'next/link';
import { CATEGORIAS } from '@/lib/categorias';

export default function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [showSub, setShowSub] = useState(false);

  return (
    <>
      {open && (
        <div className="fixed inset-0 z-40" onClick={onClose}>
          <div className="absolute inset-0 bg-black/40" />
        </div>
      )}

      <div
        className={`fixed top-0 left-0 h-full w-72 bg-white z-50 shadow-xl transform transition-transform duration-200 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b">
          <span className="font-semibold text-lg">Categorías</span>
          <button onClick={onClose} className="text-2xl leading-none cursor-pointer">&times;</button>
        </div>

        <nav className="p-4 space-y-1">
          <Link
            href="/"
            onClick={onClose}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-100 transition-colors text-sm font-medium"
          >
            🏠 Inicio
          </Link>

          <div className="border-t my-2" />

          <button
            onClick={() => setShowSub(!showSub)}
            className="w-full flex items-center justify-between gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-100 transition-colors text-sm font-medium cursor-pointer"
          >
            <span className="flex items-center gap-3">
              <span className="text-lg">📱</span>
              <span>Informática / Electrónica</span>
            </span>
            <span className="text-gray-400 text-xs">{showSub ? '▼' : '▶'}</span>
          </button>

          {showSub && (
            <div className="ml-6 mt-1 space-y-0.5">
              {CATEGORIAS.map((cat) => (
                <Link
                  key={cat.slug}
                  href={`/categoria/${cat.slug}`}
                  onClick={onClose}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors text-sm text-gray-600"
                >
                  <span>{cat.icon}</span>
                  <span>{cat.name}</span>
                </Link>
              ))}
            </div>
          )}
        </nav>
      </div>
    </>
  );
}
