import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

const EVENT_TYPES = ['view', 'click', 'favorite', 'cart', 'whatsapp'] as const;
type EventType = (typeof EVENT_TYPES)[number];

const WEIGHTS: Record<EventType, number> = {
  view: 1,
  click: 3,
  favorite: 5,
  cart: 8,
  whatsapp: 10,
};

export async function POST(req: NextRequest) {
  let body: any;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: 'JSON invalido' }, { status: 400 });
  }

  const product_external_id = body?.product_external_id;
  const store_origin = body?.store_origin;
  const event_type = body?.event_type as EventType;

  if (typeof product_external_id !== 'string' || !product_external_id) {
    return NextResponse.json({ error: 'product_external_id requerido' }, { status: 400 });
  }
  if (typeof store_origin !== 'string' || !store_origin) {
    return NextResponse.json({ error: 'store_origin requerido' }, { status: 400 });
  }
  if (!EVENT_TYPES.includes(event_type)) {
    return NextResponse.json({ error: 'event_type invalido' }, { status: 400 });
  }

  // El peso se recalcula en el server: el valor que mande el cliente se ignora.
  const { error } = await supabase.from('product_events').insert({
    product_external_id: product_external_id.slice(0, 512),
    store_origin: store_origin.slice(0, 128),
    event_type,
    weight: WEIGHTS[event_type],
    visitor_id: typeof body?.visitor_id === 'string' ? body.visitor_id.slice(0, 64) : null,
  });

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ ok: true });
}
