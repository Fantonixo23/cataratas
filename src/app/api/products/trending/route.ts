import { NextRequest, NextResponse } from 'next/server';
import { getServiceClient, COLUMNS, COLUMNS_WITH_SLUG } from '@/lib/products';

const supabase = getServiceClient();

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

async function fetchProducts(
  build: (columns: string) => any
): Promise<{ data: any[] | null; error: any }> {
  const withSlug = await build(COLUMNS_WITH_SLUG);
  if (!withSlug.error) return { data: withSlug.data, error: null };

  const without = await build(COLUMNS);
  if (without.error) {
    return { data: null, error: withSlug.error };
  }
  return { data: without.data, error: null };
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const limit = clamp(parseInt(searchParams.get('limit') || '12') || 12, 1, 30);
  const days = clamp(parseInt(searchParams.get('days') || '30') || 30, 1, 90);

  // Si trending_products() todavia no existe (migracion no corrida) caemos al
  // catalogo reciente de abajo en vez de romper la home con un 500.
  let trending: any[] | null = null;

  try {
    const res = await supabase.rpc('trending_products', { p_limit: limit, p_days: days });
    if (!res.error) trending = res.data ?? null;
  } catch {
    trending = null;
  }

  if (trending && trending.length > 0) {
    // Traemos los external_id candidatos y despues los cruzamos en memoria:
    // el par (store_origin, external_id) es la clave real del producto, pero
    // un .in() solo puede filtrar por una columna.
    const externalIds = [...new Set(trending.map((t) => t.product_external_id))];

    const { data: products, error: pErr } = await fetchProducts((columns) =>
      supabase
        .from('products')
        .select(columns)
        .in('external_id', externalIds)
        .eq('available', true)
    );

    if (pErr) {
      return NextResponse.json({ error: pErr.message }, { status: 500 });
    }

    const byKey = new Map<string, any>();
    for (const p of products || []) {
      byKey.set(`${p.store_origin}::${p.external_id}`, p);
    }

    const ranked = trending
      .map((t) => {
        const product = byKey.get(`${t.store_origin}::${t.product_external_id}`);
        return product ? { ...product, score: t.score, events: t.events } : null;
      })
      .filter(Boolean)
      .slice(0, limit);

    if (ranked.length > 0) {
      return NextResponse.json({ products: ranked, trending: true });
    }
  }

  // Sin eventos todavia (base nueva, o catalogo recien cargado): mostramos lo
  // mas reciente para que el carrusel nunca quede vacio.
  const { data: recent, error: rErr } = await fetchProducts((columns) =>
    supabase
      .from('products')
      .select(columns)
      .eq('available', true)
      .order('created_at', { ascending: false })
      .limit(limit)
  );

  if (rErr) {
    return NextResponse.json({ error: rErr.message }, { status: 500 });
  }

  return NextResponse.json({ products: recent || [], trending: false });
}
