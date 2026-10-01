'use client';

import { useState } from 'react';
import Link from 'next/link';
import { IMAGES } from '@/lib/images';

export default function CtaBackground() {
  const [imgOk, setImgOk] = useState(true);

  return (
    <section
      className="relative overflow-hidden rounded-2xl isolate"
      style={{ background: 'linear-gradient(120deg, #0b2a6b 0%, #123f9e 60%, #0e7490 100%)' }}
    >
      {imgOk && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={IMAGES.heroEcommerce}
          alt=""
          onError={() => setImgOk(false)}
          className="absolute inset-0 -z-10 h-full w-full object-cover opacity-30"
        />
      )}
      <div className="relative px-6 py-10 text-center text-white md:py-14">
        <h2 className="text-2xl md:text-3xl font-bold max-w-2xl mx-auto leading-tight">
          Encontrá tu próximo dispositivo con envío a todo Argentina
        </h2>
        <p className="text-blue-100 text-sm mt-2 max-w-xl mx-auto">
          Celulares, audio, informática y más. Consultá por WhatsApp y te ayudamos a elegir.
        </p>
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          <Link
            href="/mas-solicitados"
            className="px-5 py-2.5 rounded-lg bg-white text-blue-900 font-semibold text-sm hover:bg-blue-50 transition-colors"
          >
            Ver más solicitados
          </Link>
          <Link
            href="/marcas"
            className="px-5 py-2.5 rounded-lg bg-white/10 border border-white/30 text-white font-semibold text-sm hover:bg-white/20 transition-colors"
          >
            Explorar marcas
          </Link>
        </div>
      </div>
    </section>
  );
}
