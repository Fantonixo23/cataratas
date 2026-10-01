'use client';

export type EventType = 'view' | 'click' | 'favorite' | 'cart' | 'whatsapp';

// Mirar un producto no es lo mismo que mandarlo al carrito. El peso lo define
// el server para que se pueda re-balancear sin deploy del frontend.
const WEIGHTS: Record<EventType, number> = {
  view: 1,
  click: 3,
  favorite: 5,
  cart: 8,
  whatsapp: 10,
};

export const EVENT_WEIGHTS = WEIGHTS;

const VISITOR_KEY = 'fronterra_visitor_id';

function getVisitorId(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    let id = localStorage.getItem(VISITOR_KEY);
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem(VISITOR_KEY, id);
    }
    return id;
  } catch {
    return null;
  }
}

/**
 * Registra un evento de interes. Never throws: el tracking jamas debe romper
 * la navegacion. Usa sendBeacon porque la mayoria de los clicks navegan a otra
 * pagina y un fetch normal se cancelaria a mitad de camino.
 */
export function trackEvent(
  eventType: EventType,
  product: { external_id?: string; store_origin?: string } | null | undefined
) {
  if (typeof window === 'undefined') return;
  const externalId = product?.external_id;
  const storeOrigin = product?.store_origin;
  if (!externalId || !storeOrigin) return;

  const payload = JSON.stringify({
    event_type: eventType,
    product_external_id: externalId,
    store_origin: storeOrigin,
    weight: WEIGHTS[eventType],
    visitor_id: getVisitorId(),
  });

  try {
    if (navigator.sendBeacon) {
      navigator.sendBeacon(
        '/api/track',
        new Blob([payload], { type: 'application/json' })
      );
      return;
    }
  } catch {
    // sendBeacon puede tirar si el body es demasiado largo o la pagina se
    // esta cerrando; caemos al fetch normal.
  }

  fetch('/api/track', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: payload,
    keepalive: true,
  }).catch(() => {});
}
