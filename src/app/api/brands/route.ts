import { NextRequest, NextResponse } from 'next/server';
import { getServiceClient } from '@/lib/products';

const supabase = getServiceClient();

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

const NON_BRANDS = [
  'original', 'generico', 'genuino', 'sin marca', 's/m', 'no aplica',
  'n/a', 'otro', 'otros', 'mixto', 'varios', 'null', '-',
];

/**
 * Variantes por slug. Varias tiendas escriben la misma marca con distinta
 * capitalizacion ("SAMSUNG" y "Samsung"), y brand_slug() ya las normaliza, asi
 * que agrupamos por slug quedandonos con la variante mas corta.
 */
function mergeBySlug(rows: { brand: string; slug: string; products: number }[]) {
  const bySlug = new Map<string, { brand: string; slug: string; products: number }>();
  for (const row of rows) {
    if (!row.slug) continue;
    const current = bySlug.get(row.slug);
    if (current) {
      current.products += row.products;
      if (row.brand.length < current.brand.length) current.brand = row.brand;
    } else {
      bySlug.set(row.slug, { brand: row.brand, slug: row.slug, products: row.products });
    }
  }
  return [...bySlug.values()].sort(
    (a, b) => b.products - a.products || a.brand.localeCompare(b.brand)
  );
}

function toSlug(brand: string) {
  return brand
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const min = clamp(parseInt(searchParams.get('min') || '3') || 3, 1, 1000);
  const limit = clamp(parseInt(searchParams.get('limit') || '200') || 200, 1, 500);

  const { data, error } = await supabase.rpc('brand_counts', { p_min: min, p_limit: limit });

  if (!error && data) {
    return NextResponse.json({
      brands: mergeBySlug(
        (data as any[]).map((r) => ({
          brand: r.brand,
          slug: r.slug,
          products: Number(r.products),
        }))
      ),
    });
  }

  // brand_counts() todavia no existe en la base: replicamos el agrupado
  // leyendo la columna brand por paginas. Es mas pesado que el GROUP BY de
  // Postgres, asi que este camino es solo el puente hasta correr la migracion.
  if (error && (error.code === '42883' || error.code === 'PGRST202' || /function/i.test(error.message || ''))) {
    const CHUNK = 1000;
    const MAX_ROWS = 100_000;

    const { count } = await supabase
      .from('products')
      .select('id', { count: 'exact', head: true });

    const total = Math.min(count || 0, MAX_ROWS);
    const counts = new Map<string, number>();

    for (let from = 0; from < total; from += CHUNK) {
      const to = Math.min(from + CHUNK, total) - 1;
      const { data: rows, error: gErr } = await supabase
        .from('products')
        .select('brand')
        .eq('available', true)
        .not('brand', 'is', null)
        .range(from, to);

      if (gErr) {
        return NextResponse.json({ error: gErr.message }, { status: 500 });
      }

      for (const row of rows || []) {
        const raw = String(row.brand).trim();
        if (raw.length < 2 || raw.length > 40) continue;
        if (NON_BRANDS.includes(raw.toLowerCase())) continue;
        const key = raw.toLowerCase();
        counts.set(key, (counts.get(key) || 0) + 1);
      }
    }

    const brands = [...counts.entries()]
      .filter(([, n]) => n >= min)
      .map(([brand, n]) => ({ brand, slug: toSlug(brand), products: n }))
      .filter((b) => b.slug)
      .sort((a, b) => b.products - a.products || a.brand.localeCompare(b.brand))
      .slice(0, limit);

    return NextResponse.json({ brands });
  }

  return NextResponse.json({ error: error?.message || 'No se pudieron leer las marcas' }, { status: 500 });
}
