import { NextRequest, NextResponse } from 'next/server';
import { createServerClient } from '@supabase/ssr';

function fromReq(req: NextRequest) {
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) { return req.cookies.get(name)?.value },
        set() {},
        remove() {},
      },
    }
  );
}

export async function GET(req: NextRequest) {
  const supabase = fromReq(req);
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ items: [] });

  const { data } = await supabase
    .from('cart_items')
    .select('*')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false });

  return NextResponse.json({ items: data || [] });
}

export async function POST(req: NextRequest) {
  const supabase = fromReq(req);
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'No autorizado' }, { status: 401 });

  const body = await req.json();
  const { product_external_id, product_name, product_image, product_price, store_origin, source_url } = body;

  const { error } = await supabase.from('cart_items').insert({
    user_id: user.id,
    product_external_id,
    product_name,
    product_image,
    product_price,
    store_origin,
    source_url,
  });

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ success: true });
}

export async function DELETE(req: NextRequest) {
  const supabase = fromReq(req);
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'No autorizado' }, { status: 401 });

  const { searchParams } = new URL(req.url);
  const id = searchParams.get('id');
  if (id) {
    await supabase.from('cart_items').delete().eq('id', id).eq('user_id', user.id);
  }

  return NextResponse.json({ success: true });
}
