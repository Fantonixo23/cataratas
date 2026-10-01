'use client';

import { useState } from 'react';
import { IMAGES } from '@/lib/images';

const DESTACADOS = [
  { icon: '📦', title: 'Gran variedad', text: 'De todo un poco en un solo lugar' },
  { icon: '⚡', title: 'Envíos a todo el país', text: 'Llegamos donde estés en Argentina' },
  { icon: '💬', title: 'Atención cercana', text: 'Te acompañamos en cada compra' },
];

export default function QuienesSomos() {
  const [imgOk, setImgOk] = useState(true);

  return (
    <section
      id="quienes-somos"
      className="relative overflow-hidden rounded-2xl isolate scroll-mt-24"
      style={{ background: 'linear-gradient(135deg, #0b2a6b 0%, #123f9e 45%, #0e7490 100%)' }}
    >
      {imgOk && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={IMAGES.ciudadDelEste}
          alt="Ciudad del Este, Paraguay"
          onError={() => setImgOk(false)}
          className="absolute inset-0 -z-10 h-full w-full object-cover opacity-45"
        />
      )}
      <div
        className="absolute inset-0 -z-10"
        style={{
          backgroundImage:
            'radial-gradient(circle at 20% 20%, rgba(255,255,255,.14) 0, transparent 45%), radial-gradient(circle at 80% 70%, rgba(255,255,255,.10) 0, transparent 40%)',
        }}
      />

      <div className="px-6 py-12 md:px-12 md:py-16 text-white">
        <span className="inline-block text-xs font-semibold uppercase tracking-widest text-blue-200">
          Quiénes somos
        </span>
        <h2 className="mt-2 text-2xl md:text-3xl font-bold max-w-2xl leading-tight">
          Una empresa de Ciudad del Este con una propuesta simple
        </h2>

        <div className="mt-4 max-w-3xl space-y-3 text-blue-50/95 text-sm md:text-base leading-relaxed">
          <p>
            Somos una empresa de Ciudad del Este, Paraguay, con una propuesta simple: ofrecerte una
            gran variedad de productos a buenos precios. Tenemos de todo un poco, pero la{' '}
            <strong className="text-white">electrónica es nuestra especialidad</strong>: celulares,
            accesorios, audio, tecnología y mucho más.
          </p>
          <p>
            Trabajamos con <strong className="text-white">envíos a todo el territorio argentino</strong>,
            para que estés donde estés puedas acceder a lo mejor de la zona comercial más reconocida
            de la región. Nos importa tu confianza, por eso te acompañamos en cada compra con
            atención cercana y productos de calidad.
          </p>
          <p className="text-white font-semibold text-base">Comprá fácil, recibí en tu casa.</p>
        </div>

        <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-3">
          {DESTACADOS.map((d) => (
            <div
              key={d.title}
              className="flex items-start gap-3 rounded-xl bg-white/10 backdrop-blur-sm border border-white/15 p-4"
            >
              <span className="text-2xl leading-none" aria-hidden>{d.icon}</span>
              <div>
                <p className="font-semibold text-sm">{d.title}</p>
                <p className="text-xs text-blue-100/90 mt-0.5">{d.text}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
