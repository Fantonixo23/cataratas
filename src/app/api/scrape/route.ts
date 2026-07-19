import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export const runtime = 'nodejs';

export async function GET(req: NextRequest) {
  const q = req.nextUrl.searchParams.get('q')?.trim();

  try {
    let query = supabase
      .from('products')
      .select('name, price, image_url, source_url, store_origin, external_id')
      .order('created_at', { ascending: false });

    if (q && q.length >= 2) {
      query = query.ilike('name', `%${q}%`).limit(50);
    } else {
      query = query.limit(200);
    }

    const { data, error } = await query;

    if (error) throw error;

    return NextResponse.json({ products: data || [] });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ products: [], error: message }, { status: 500 });
  }
}
