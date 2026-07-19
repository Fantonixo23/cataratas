import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export async function GET(req: NextRequest) {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ items: [] });

  const { data } = await supabase
    .from('favorites')
    .select('*')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false });

  return NextResponse.json({ items: data || [] });
}

export async function POST(req: NextRequest) {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'No autorizado' }, { status: 401 });

  const body = await req.json();
  const { product_external_id, product_name, product_image, product_price, store_origin } = body;

  const { error } = await supabase.from('favorites').upsert({
    user_id: user.id,
    product_external_id,
    product_name,
    product_image,
    product_price,
    store_origin,
  }, { onConflict: 'user_id,product_external_id' });

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ success: true });
}

export async function DELETE(req: NextRequest) {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'No autorizado' }, { status: 401 });

  const { searchParams } = new URL(req.url);
  const id = searchParams.get('id');

  if (id) {
    await supabase.from('favorites').delete().eq('id', id).eq('user_id', user.id);
  } else {
    const product_external_id = searchParams.get('product_external_id');
    if (product_external_id) {
      await supabase.from('favorites').delete().eq('product_external_id', product_external_id).eq('user_id', user.id);
    }
  }

  return NextResponse.json({ success: true });
}
