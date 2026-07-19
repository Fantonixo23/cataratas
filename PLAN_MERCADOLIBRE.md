# Plan Maestro: Catarata — Comparador con API de MercadoLibre Argentina

> Buscador con diseño 100% propio (marca, colores, UI) que por detrás consulta la API oficial de MercadoLibre Argentina. Precio oculto en el grid de resultados, reemplazado por un botón "Consultar por WhatsApp" con mensaje prellenado. Se aclara al usuario que los resultados provienen del buscador de MercadoLibre Argentina (transparencia de origen).

Este plan **reemplaza** el enfoque anterior de scraping a Nissei/Visaovip — ya no hace falta scraping ni motor de búsqueda propio (Meilisearch), porque MercadoLibre ya expone una API oficial con buscador, filtros y orden por relevancia/precio incluidos.

### Dos piezas separadas, no una sola

Este plan tiene **dos partes independientes** que cumplen roles distintos:

1. **El buscador en vivo (Fases 1-6)**: la herramienta que usa la gente que ya está en tu web. Escriben "iphone pro max", el buscador le pega a la API de MercadoLibre en el momento, y aparecen resultados con el botón de WhatsApp. Es el corazón del producto.
2. **Las páginas de guía / SEO (Fase 7)**: el canal de entrada desde Google. El buscador interactivo por sí solo casi no lo indexa Google (depende de una interacción del usuario) y, aunque lo indexara, competiría en desventaja directa contra el propio MercadoLibre. Las páginas de guía tienen contenido propio (texto, consejos, contexto paraguayo) que Google sí puede posicionar, y desde ahí el usuario entra y usa el buscador en vivo.

```
Google → página de guía (texto propio, SEO) → usuario entra al sitio
                                                      ↓
                                    usa el buscador en vivo con la API
                                    (escribe "iphone pro max", ve resultados)
                                                      ↓
                                          botón "Consultar por WhatsApp"
```

El buscador no se reemplaza ni se toca — sigue funcionando igual que en las Fases 1-6. Las páginas de guía son contenido adicional para que el sitio también reciba tráfico de búsqueda orgánica.

---

## 0. Arquitectura general

```
Usuario escribe "iphone" en catarata.shop
        ↓
Tu backend (Next.js API route)
        ↓  (con access_token de MercadoLibre)
GET https://api.mercadolibre.com/sites/MLA/search?q=iphone
        ↓
JSON con productos, filtros y orden disponibles
        ↓
Tu backend normaliza el formato (oculta precio, arma mensaje de WhatsApp)
        ↓
Frontend Next.js con TU diseño → grid de tarjetas → botón "Consultar por WhatsApp"
```

**Stack:**

| Capa | Tecnología |
|---|---|
| Frontend/Backend | Next.js 14 (App Router) + TypeScript + Tailwind |
| Fuente de datos | API oficial de MercadoLibre Argentina (`api.mercadolibre.com`) |
| Autenticación con la API | OAuth 2.0 (access_token + refresh_token) |
| Guardado del token | Supabase (tabla `ml_tokens`) |
| Hosting | Vercel |
| Dominio | catarata.shop |

---

## Fase 1 — Registrar tu aplicación en MercadoLibre (Día 1)

1. Crear cuenta en [developers.mercadolibre.com.ar](https://developers.mercadolibre.com.ar) (podés usar tu cuenta normal de MercadoLibre o crear una nueva)
2. Ir a **"Mis aplicaciones"** → **"Crear nueva aplicación"**
3. Completar:
   - Nombre de la app: `Catarata`
   - Redirect URI: `https://catarata.shop/api/auth/mercadolibre/callback` (o `http://localhost:3000/...` para probar en local)
   - Tópicos/permisos: los básicos de lectura de ítems y búsqueda
4. Guardar el **Client ID** y **Client Secret** que te da la plataforma

**Checkpoint:** tenés `CLIENT_ID` y `CLIENT_SECRET` guardados.

---

## Fase 2 — Flujo de autorización OAuth (Día 1-2)

MercadoLibre requiere un `access_token` obtenido vía OAuth para poder usar el buscador. Esto se hace **una sola vez** (con renovación automática después vía `refresh_token`), no en cada búsqueda de usuario.

### 2.1 Variables de entorno (`.env.local`)

```
ML_CLIENT_ID=tu_client_id
ML_CLIENT_SECRET=tu_client_secret
ML_REDIRECT_URI=https://catarata.shop/api/auth/mercadolibre/callback
NEXT_PUBLIC_SUPABASE_URL=tu_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=tu_anon_key
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key
```

### 2.2 Tabla en Supabase para guardar el token

```sql
create table ml_tokens (
  id int primary key default 1,       -- una sola fila, siempre la misma
  access_token text not null,
  refresh_token text not null,
  expires_at timestamp not null
);
```

### 2.3 Ruta para iniciar el login con MercadoLibre (`src/app/api/auth/mercadolibre/route.ts`)

```ts
import { NextResponse } from 'next/server';

export async function GET() {
  const url = `https://auth.mercadolibre.com.ar/authorization?response_type=code&client_id=${process.env.ML_CLIENT_ID}&redirect_uri=${process.env.ML_REDIRECT_URI}`;
  return NextResponse.redirect(url);
}
```

### 2.4 Callback que intercambia el código por el token (`src/app/api/auth/mercadolibre/callback/route.ts`)

```ts
import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function GET(req: NextRequest) {
  const code = req.nextUrl.searchParams.get('code');
  if (!code) return NextResponse.json({ error: 'Falta el code' }, { status: 400 });

  const res = await fetch('https://api.mercadolibre.com/oauth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      client_id: process.env.ML_CLIENT_ID!,
      client_secret: process.env.ML_CLIENT_SECRET!,
      code,
      redirect_uri: process.env.ML_REDIRECT_URI!,
    }),
  });

  const data = await res.json();
  if (!res.ok) return NextResponse.json({ error: data }, { status: 400 });

  const expiresAt = new Date(Date.now() + data.expires_in * 1000).toISOString();

  await supabase.from('ml_tokens').upsert({
    id: 1,
    access_token: data.access_token,
    refresh_token: data.refresh_token,
    expires_at: expiresAt,
  });

  return NextResponse.redirect('https://catarata.shop/admin?ml_conectado=1');
}
```

### 2.5 Probar el flujo

1. Entrar a `catarata.shop/api/auth/mercadolibre` (te redirige a loguearte en MercadoLibre y autorizar la app)
2. Después de aceptar, vuelve al callback, guarda el token en Supabase, y te redirige al admin

**Checkpoint:** en la tabla `ml_tokens` de Supabase ves una fila con `access_token` guardado.

---

## Fase 3 — Renovación automática del token (Día 2)

Los `access_token` de MercadoLibre expiran (normalmente en unas horas). Se renuevan con el `refresh_token`, sin que el usuario tenga que volver a loguearse.

### `src/lib/mercadolibre/token.ts`

```ts
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function getValidAccessToken(): Promise<string> {
  const { data, error } = await supabase.from('ml_tokens').select('*').eq('id', 1).single();
  if (error || !data) throw new Error('No hay token de MercadoLibre configurado. Autorizá la app primero.');

  const isExpired = new Date(data.expires_at).getTime() < Date.now() + 60_000; // margen de 1 min

  if (!isExpired) return data.access_token;

  // Renovar con refresh_token
  const res = await fetch('https://api.mercadolibre.com/oauth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      client_id: process.env.ML_CLIENT_ID!,
      client_secret: process.env.ML_CLIENT_SECRET!,
      refresh_token: data.refresh_token,
    }),
  });

  const refreshed = await res.json();
  if (!res.ok) throw new Error('No se pudo renovar el token de MercadoLibre');

  const expiresAt = new Date(Date.now() + refreshed.expires_in * 1000).toISOString();

  await supabase.from('ml_tokens').update({
    access_token: refreshed.access_token,
    refresh_token: refreshed.refresh_token,
    expires_at: expiresAt,
  }).eq('id', 1);

  return refreshed.access_token;
}
```

**Checkpoint:** llamando a `getValidAccessToken()` dos veces, una antes y otra después de forzar el vencimiento, siempre devuelve un token válido sin intervención manual.

---

## Fase 4 — Endpoint de búsqueda que consulta MercadoLibre (Día 3)

### 4.1 Tipos (`src/lib/mercadolibre/types.ts`)

```ts
export interface CataraProduct {
  id: string;
  name: string;
  image_url: string | null;
  permalink_ml: string;       // link original, no se muestra al usuario, solo referencia interna
  whatsapp_message: string;   // mensaje ya armado, listo para el link de WhatsApp
}
```

### 4.2 Cliente de búsqueda (`src/lib/mercadolibre/search.ts`)

```ts
import { getValidAccessToken } from './token';
import { CataraProduct } from './types';

const WHATSAPP_NUMBER = '5959XXXXXXXX'; // reemplazar por tu número real

export async function searchMercadoLibre(
  query: string,
  opts?: { sort?: 'price_asc' | 'price_desc'; limit?: number }
): Promise<CataraProduct[]> {
  const token = await getValidAccessToken();

  const params = new URLSearchParams({
    q: query,
    limit: String(opts?.limit ?? 20),
  });
  if (opts?.sort) params.set('sort', opts.sort);

  const res = await fetch(`https://api.mercadolibre.com/sites/MLA/search?${params}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    throw new Error(`Error consultando MercadoLibre: ${res.status}`);
  }

  const data = await res.json();

  return data.results.map((item: any): CataraProduct => ({
    id: item.id,
    name: item.title,
    image_url: item.thumbnail?.replace('http://', 'https://') ?? null,
    permalink_ml: item.permalink,
    whatsapp_message: buildWhatsappMessage(item.title),
  }));
}

function buildWhatsappMessage(productName: string): string {
  const text = `Hola! quisiera saber sobre "${productName}" y su precio, muchas gracias :D`;
  return `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(text)}`;
}
```

> Nota: `item.price` viene disponible en la respuesta de la API si más adelante querés usarlo para ordenar internamente (por ejemplo "más baratos primero" sin mostrar el número), aunque no lo estemos exponiendo al frontend en este plan.

### 4.3 Endpoint (`src/app/api/search/route.ts`)

```ts
import { NextRequest, NextResponse } from 'next/server';
import { searchMercadoLibre } from '@/lib/mercadolibre/search';

export const runtime = 'nodejs';

export async function GET(req: NextRequest) {
  const q = req.nextUrl.searchParams.get('q')?.trim();
  const sort = req.nextUrl.searchParams.get('sort') as 'price_asc' | 'price_desc' | null;

  if (!q || q.length < 2) {
    return NextResponse.json({ products: [] });
  }

  try {
    const products = await searchMercadoLibre(q, { sort: sort ?? undefined });
    return NextResponse.json({ products });
  } catch (err) {
    return NextResponse.json({ products: [], error: String(err) }, { status: 500 });
  }
}
```

**Checkpoint:** `catarata.shop/api/search?q=iphone` devuelve JSON con productos, sin precio, con `whatsapp_message` ya armado.

---

## Fase 5 — Frontend: buscador con diseño propio (Día 4-5)

### 5.1 Buscador con filtro de orden (`src/components/SearchBar.tsx`)

```tsx
'use client';

import { useEffect, useState } from 'react';
import ProductCard from './ProductCard';

type SortOption = '' | 'price_asc' | 'price_desc';

export default function SearchBar() {
  const [query, setQuery] = useState('');
  const [sort, setSort] = useState<SortOption>('');
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (query.trim().length < 2) { setProducts([]); return; }
    const timeout = setTimeout(async () => {
      setLoading(true);
      const params = new URLSearchParams({ q: query });
      if (sort) params.set('sort', sort);
      const res = await fetch(`/api/search?${params}`);
      const data = await res.json();
      setProducts(data.products || []);
      setLoading(false);
    }, 350);
    return () => clearTimeout(timeout);
  }, [query, sort]);

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Buscar iPhone, Samsung, notebook..."
        className="w-full p-3 border rounded-lg"
      />

      <div className="flex gap-2 mt-2">
        <button onClick={() => setSort('')} className={`text-sm px-3 py-1 rounded ${sort === '' ? 'bg-black text-white' : 'bg-gray-100'}`}>
          Relevancia
        </button>
        <button onClick={() => setSort('price_asc')} className={`text-sm px-3 py-1 rounded ${sort === 'price_asc' ? 'bg-black text-white' : 'bg-gray-100'}`}>
          Más baratos
        </button>
        <button onClick={() => setSort('price_desc')} className={`text-sm px-3 py-1 rounded ${sort === 'price_desc' ? 'bg-black text-white' : 'bg-gray-100'}`}>
          Más caros
        </button>
      </div>

      {loading && <p className="text-sm text-gray-400 mt-2">Buscando...</p>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
        {products.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </div>
  );
}
```

> El orden "más baratos/más caros" se lo pasamos directo a la API de MercadoLibre (`sort=price_asc`), que ordena los resultados reales por precio aunque nosotros no mostremos el número en pantalla.

### 5.2 Tarjeta con precio oculto y botón de WhatsApp (`src/components/ProductCard.tsx`)

```tsx
export default function ProductCard({ product }: { product: any }) {
  return (
    <div className="border rounded-lg p-3 flex flex-col">
      {product.image_url && (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={product.image_url} alt={product.name} className="w-full h-32 object-contain" />
      )}
      <h3 className="text-sm font-medium mt-2 line-clamp-2">{product.name}</h3>

      {/* Precio intencionalmente oculto */}

      <a
        href={product.whatsapp_message}
        target="_blank"
        rel="noopener noreferrer"
        className="block text-center bg-green-600 hover:bg-green-700 text-white text-base font-semibold rounded-lg py-3 mt-3 transition-colors"
      >
        Consultar precio por WhatsApp
      </a>
    </div>
  );
}
```

El link ya incluye el mensaje armado en el backend:
`Hola! quisiera saber sobre "iPhone 13 128GB" y su precio, muchas gracias :D`

### 5.3 Aviso de transparencia de origen (footer o debajo del buscador)

```tsx
<p className="text-xs text-gray-400 mt-6 text-center">
  Los resultados de búsqueda provienen del buscador de MercadoLibre Argentina.
  Catarata no es una tienda ni garantiza disponibilidad o precio final; para
  cerrar tu compra te contactamos por WhatsApp.
</p>
```

Esto es lo que hablamos antes: tu diseño es 100% propio, pero dejás clara la fuente de los datos — te protege a vos legalmente y cumple con lo que suelen pedir los términos de uso de la API.

**Checkpoint:** en `localhost:3000` buscás "iphone", cambiás entre "Relevancia" / "Más baratos" / "Más caros", y cada tarjeta muestra el botón verde grande sin precio, que abre WhatsApp con el mensaje correcto.

---

## Fase 6 — Deploy (Día 5-6)

```bash
git add .
git commit -m "feat: integración con API de MercadoLibre, precio oculto, botón WhatsApp"
git push
```

- Confirmar en Vercel las variables: `ML_CLIENT_ID`, `ML_CLIENT_SECRET`, `ML_REDIRECT_URI`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- Actualizar el `Redirect URI` en la app de MercadoLibre a la URL real de producción
- Una vez en producción, entrar una vez a `catarata.shop/api/auth/mercadolibre` para autorizar la app en el entorno real y guardar el primer token

**Checkpoint:** `https://catarata.shop` funciona igual que en local, con dominio propio y HTTPS.

---

## Fase 7 — SEO: páginas de guía y contenido propio (Día 6-10)

### 7.1 Por qué el buscador solo no alcanza para SEO

- El buscador interactivo (`SearchBar.tsx`) pide datos en el navegador recién cuando el usuario escribe algo — Google no interactúa con tu web, así que nunca ve esos resultados.
- Aunque los indexara, los productos que trae la API **ya están indexados en mercadolibre.com.ar**, un dominio de mucha más autoridad. Competir con el mismo contenido copiado es una pelea perdida de antemano.
- La solución no es "hacer que Google indexe el buscador", sino crear páginas separadas con **contenido propio** que Google sí puede posicionar, y que usan el buscador/la API solo como apoyo visual adentro.

### 7.2 Qué páginas crear

Un puñado de páginas de guía/categoría (5-10 para arrancar, no una por cada producto):

```
/guia-comprar-iphone-paraguay
/guia-comprar-samsung-paraguay
/tienda-electronica-ciudad-del-este
/como-comprar-en-mercadolibre-desde-paraguay
```

Apuntadas a keywords realistas para tu nicho: "comprar iphone paraguay", "tienda electrónica ciudad del este", "electrónica paraguay whatsapp" — terreno donde compites contra comparadores como Compras Paraguay, no contra MercadoLibre directamente.

### 7.3 Estructura de cada página

Cada página combina:
1. **Texto propio y sustancial** (300-600 palabras): contexto del producto, cuota de importación, consejos de compra, diferencias entre modelos — contenido que solo vos tenés
2. **Un bloque de "precios de referencia actuales"**: 4-8 tarjetas de producto renderizadas en el servidor (no client-side) con datos en vivo de la API de MercadoLibre, como apoyo visual del artículo
3. **Botón de WhatsApp** al final

### 7.4 Ejemplo de página con datos renderizados en servidor (`src/app/guia-comprar-iphone-paraguay/page.tsx`)

```tsx
import { searchMercadoLibre } from '@/lib/mercadolibre/search';
import ProductCard from '@/components/ProductCard';

export const revalidate = 3600; // regenera la página cada 1 hora (ISR)

export const metadata = {
  title: 'Guía 2026: cómo comprar un iPhone en Paraguay y cuánto cuesta | Catarata',
  description: 'Guía completa para comprar iPhone en Paraguay: modelos disponibles, cuota de importación y precios de referencia actualizados.',
};

export default async function GuiaIphonePage() {
  const products = await searchMercadoLibre('iphone', { limit: 6 });

  return (
    <main className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-semibold">Guía 2026: cómo comprar un iPhone en Paraguay</h1>

      <p className="mt-4 text-gray-700">
        {/* Texto propio: modelos disponibles, diferencias entre versiones,
            qué revisar antes de comprar (nuevo vs. reacondicionado), etc. */}
      </p>

      <p className="mt-4 text-gray-700">
        {/* Texto propio: cuota de importación para compradores argentinos/
            brasileños, qué documentación llevar, límites vigentes. */}
      </p>

      <h2 className="text-xl font-medium mt-8">Precios de referencia actuales</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4">
        {products.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </main>
  );
}
```

> Clave: esta página usa `async function` de servidor (Server Component), no `useEffect` en el navegador — así el HTML que recibe Google ya viene con los productos adentro. `revalidate = 3600` hace que Next.js regenere la página cada hora (ISR), manteniéndola razonablemente fresca sin pedirle datos a la API en cada visita.

### 7.5 SEO técnico

- **Sitemap** (`next-sitemap` o un `sitemap.ts` nativo de Next.js) listando todas las páginas de guía
- **`robots.txt`**: permitir indexar las páginas de guía, bloquear `/api/*` y `/admin`
- **Datos estructurados Schema.org** tipo `Article` para las páginas de guía (no `Product` con precio, ya que el precio está oculto)
- **Mobile-first**: la mayoría del tráfico paraguayo es celular, confirmar que las tarjetas y botones se vean bien en pantallas chicas

### 7.6 SEO local y off-page

- Perfil de **Google Business Profile** si hay algún punto de atención físico
- Mencionar explícitamente ciudades/países objetivo en el texto (Paraguay, Ciudad del Este, Argentina/Brasil si apuntás a compradores fronterizos)
- Presencia en redes (Instagram/TikTok) para generar tráfico directo, como hace Compras Paraguay — el SEO orgánico crece en paralelo, no en lugar de esto

**Checkpoint:** las páginas de guía cargan con el texto y los productos ya presentes en el HTML inicial (confirmable con "Ver código fuente" del navegador, sin ejecutar JavaScript), y aparecen en el `sitemap.xml`.

---

## Checklist de "funciona al 100%"

- [ ] App creada en developers.mercadolibre.com.ar con Client ID y Secret
- [ ] Flujo OAuth completo: autorización → callback → token guardado en Supabase
- [ ] Renovación automática de token probada (no requiere reloguearse)
- [ ] Endpoint `/api/search` devuelve productos reales de MercadoLibre sin precio expuesto
- [ ] Filtros de orden (relevancia / más baratos / más caros) funcionando
- [ ] Botón "Consultar precio por WhatsApp" con mensaje correcto por producto
- [ ] Aviso de transparencia de origen visible en la página
- [ ] Deploy en Vercel con dominio propio y variables de entorno cargadas
- [ ] Al menos 3-5 páginas de guía creadas, con texto propio + bloque de productos renderizado en servidor
- [ ] `sitemap.xml` y `robots.txt` configurados, páginas de guía indexables
- [ ] Confirmado que el HTML inicial de las páginas de guía ya trae el texto y los productos (sin depender de JavaScript para aparecer)

---

## Notas finales

- **Precio internamente disponible**: aunque no se muestra, `item.price` sigue llegando en la respuesta de la API — útil si más adelante querés lógica interna (ej. descartar productos fuera de cierto rango) sin exponerlo en pantalla.
- **Límites de uso de la API**: MercadoLibre aplica límites de rate (requests por minuto/hora) según el tipo de aplicación. Con el volumen de un comparador chico no debería ser un problema, pero es bueno revisarlo en la documentación oficial si el tráfico crece mucho.
- **Términos de uso**: antes de escalar esto a un negocio con volumen real, vale la pena revisar los términos de la API de MercadoLibre sobre uso de datos en comparadores de terceros, para confirmar que este modelo (mostrar resultados con marca propia, aclarando el origen, sin vender directo) está dentro de lo permitido.
