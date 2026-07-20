import Link from 'next/link';

const socials = [
  { name: 'Facebook', href: '#', icon: 'f' },
  { name: 'Instagram', href: '#', icon: 'ig' },
  { name: 'TikTok', href: '#', icon: 'tt' },
  { name: 'Telegram', href: '#', icon: 'tg' },
  { name: 'WhatsApp', href: '#', icon: 'wa' },
];

export default function Footer() {
  return (
    <footer className="bg-blue-900 text-white mt-16">
      <div className="max-w-5xl mx-auto px-4 py-10 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <h3 className="text-lg font-bold mb-2">Catarata</h3>
          <p className="text-sm text-blue-200">
            Buscador de productos en Ciudad del Este, Paraguay. Compará precios y consultá por WhatsApp.
          </p>
        </div>

        <div>
          <h3 className="text-lg font-bold mb-2">Redes</h3>
          <div className="flex gap-3">
            {socials.map((s) => (
              <Link
                key={s.name}
                href={s.href}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-blue-800 hover:bg-blue-700 rounded-lg px-3 py-1.5 text-sm transition-colors"
                title={s.name}
              >
                {s.name}
              </Link>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-bold mb-2">Ubicación</h3>
          <div className="rounded-lg overflow-hidden border border-blue-700">
            <iframe
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d115061.08838440112!2d-54.65907308308881!3d-25.509608105016634!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x94328cc0cea42a3b%3A0x6de2c48a1a7e58a1!2sCiudad%20del%20Este%2C%20Paraguay!5e0!3m2!1ses-419!2s!4v1!4m1!1s0x94328cc0cea42a3b%3A0x6de2c48a1a7e58a1"
              width="100%"
              height="160"
              style={{ border: 0 }}
              allowFullScreen
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
              title="Ubicación Ciudad del Este"
            />
          </div>
          <p className="text-xs text-blue-200 mt-1">Microcentro, Ciudad del Este, Paraguay</p>
        </div>
      </div>

      <div className="border-t border-blue-800 text-center text-xs text-blue-300 py-4">
        Los resultados provienen de tiendas asociadas. Catarata no es una tienda ni garantiza disponibilidad o precio final.
      </div>
    </footer>
  );
}
