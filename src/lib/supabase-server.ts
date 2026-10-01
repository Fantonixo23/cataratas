import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/ssr';

// FIX (bug 3): api/favorites y api/cart usaban un helper propio con
// set() {} y remove() {} vacios, asi que cuando Supabase refrescaba el
// access token el cookie nuevo se descartaba y el usuario quedaba
// deslogueado al siguiente request.
//
// Ahora se usa el store oficial de Next. cookies() es mutable dentro de
// Route Handlers, asi que los refreshes se propagan a la respuesta.
export async function createServerSupabase() {
  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          for (const { name, value, options } of cookiesToSet) {
            cookieStore.set(name, value, options);
          }
        },
      },
    }
  );
}
