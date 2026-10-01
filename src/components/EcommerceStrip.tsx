'use client';

import { useState } from 'react';
import { IMAGES } from '@/lib/images';

const PANELS = [
  {
    key: 'personas' as const,
    image: IMAGES.franjaPersonas,
    icon: '🛍️',
    title: 'Comprá tranquilo',
    text: 'Elegí lo que buscás y te lo preparamos.',
    gradient: 'linear-gradient(135deg, #0f766e 0%, #0e7490 100%)',
  },
  {
    key: 'envios' as const,
    image: IMAGES.franjaEnvios,
    icon: '🚚',
    title: 'Envíos a todo el país',
    text: 'Ciudades y provincias de Argentina.',
    gradient: 'linear-gradient(135deg, #b45309 0%, #c2410c 100%)',
  },
  {
    key: 'comercio' as const,
    image: IMAGES.franjaComercio,
    icon: '🏬',
    title: 'Ciudad del Este',
    text: 'Lo mejor de la zona comercial, en tu puerta.',
    gradient: 'linear-gradient(135deg, #1e3a8a 0%, #4338ca 100%)',
  },
];

function Panel({ panel }: { panel: (typeof PANELS)[number] }) {
  const [imgOk, setImgOk] = useState(true);

  return (
    <div
      className="relative overflow-hidden rounded-2xl min-h-36 isolate"
      style={{ background: panel.gradient }}
    >
      {imgOk && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={panel.image}
          alt={panel.title}
          onError={() => setImgOk(false)}
          className="absolute inset-0 -z-10 h-full w-full object-cover opacity-50"
        />
      )}
      <div
        className="absolute inset-0 -z-10"
        style={{ background: 'linear-gradient(to top, rgba(0,0,0,.72) 0%, rgba(0,0,0,.25) 60%, transparent 100%)' }}
      />
      <div className="flex h-full flex-col justify-end p-5 text-white">
        <span className="text-2xl" aria-hidden>{panel.icon}</span>
        <h3 className="font-semibold mt-1">{panel.title}</h3>
        <p className="text-xs text-white/85">{panel.text}</p>
      </div>
    </div>
  );
}

export default function EcommerceStrip() {
  return (
    <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {PANELS.map((p) => (
        <Panel key={p.key} panel={p} />
      ))}
    </section>
  );
}
