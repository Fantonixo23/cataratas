import { NextRequest, NextResponse } from 'next/server';
import { getServiceClient, COLUMNS, COLUMNS_WITH_SLUG, isMissingColumn } from '@/lib/products';

const supabase = getServiceClient();

type Filter = { category: string; brand: string };
type Result = { data: any[] | null; error: any; count: number | null };

function run(columns: string, filter: Filter, from: number, to: number, bySlug: boolean) {
  let q = supabase.from('products').select(columns, { count: 'exact' });
  if (filter.category) q = q.eq('category', filter.category);
  // Degradacion previa a la migracion: comparamos contra el texto crudo.
  if (filter.brand) q = bySlug ? q.eq('brand_slug', filter.brand) : q.eq('brand', filter.brand);
  return q.order('created_at', { ascending: false }).range(from, to) as PromiseLike<Result>;
}

/**
 * brand_slug es una Generated Column. Antes de correr esa parte de
 * supabase-schema.sql la consulta falla con 42703, asi que reintentamos contra
 * la columna brand cruda. Solo pierde el matching exacto del slug, la pagina
 * sigue funcionando.
 */
export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const filter: Filter = {
    category: searchParams.get('category') || '',
    brand: searchParams.get('brand') || '',
  };
  const page = Math.max(1, parseInt(searchParams.get('page') || '1'));
  const limit = Math.min(50, Math.max(1, parseInt(searchParams.get('limit') || '20')));
  const from = (page - 1) * limit;
  const to = from + limit - 1;

  let result = await run(COLUMNS_WITH_SLUG, filter, from, to, true);
  if (result.error && isMissingColumn(result.error)) {
    result = await run(COLUMNS, filter, from, to, false);
  }

  if (result.error) {
    return NextResponse.json({ error: result.error.message }, { status: 500 });
  }

  const count = result.count || 0;
  return NextResponse.json({
    products: result.data || [],
    total: count,
    page,
    limit,
    totalPages: Math.ceil(count / limit),
  });
}
