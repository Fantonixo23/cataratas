import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const q = searchParams.get('q') || '';
  const limit = Math.min(20, Math.max(1, parseInt(searchParams.get('limit') || '6')));

  if (!q || q.length < 2) {
    return NextResponse.json({ products: [] });
  }

  const { data, error } = await supabase
    .from('products')
    .select('name, price, image_url, source_url, store_origin, external_id, category')
    .ilike('name', `%${q}%`)
    .order('created_at', { ascending: false })
    .limit(limit);

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ products: data || [] });
}
