import { createClient, SupabaseClient } from '@supabase/supabase-js';

const COLUMNS =
  'name, price, image_url, source_url, store_origin, external_id, category, brand';

// brand_slug es una Generated Column que agrega supabase-schema.sql. Si el
// proyecto todavia no corrio esa parte del script, consultarla tira 42703 y
// dejaria en blanco toda la home. Por eso caemos a un select sin ella.
const COLUMNS_WITH_SLUG = `${COLUMNS}, brand_slug`;

export function getServiceClient(): SupabaseClient {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
}

function isMissingColumn(error: any) {
  return (
    error?.code === '42703' ||
    error?.code === 'PGRST204' ||
    /column .* does not exist/i.test(error?.message || '')
  );
}

export { COLUMNS, COLUMNS_WITH_SLUG, isMissingColumn };
