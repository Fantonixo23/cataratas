'use client';

import { Suspense, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { supabase } from '@/lib/supabase-client';

function CallbackInner() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const code = searchParams.get('code');
    const hash = window.location.hash;

    if (code) {
      supabase.auth.exchangeCodeForSession(code).then(() => {
        window.location.href = '/';
      });
    } else if (hash && hash.includes('access_token')) {
      const params = new URLSearchParams(hash.slice(1));
      supabase.auth.setSession({
        access_token: params.get('access_token') ?? '',
        refresh_token: params.get('refresh_token') ?? '',
      }).then(() => {
        window.location.href = '/';
      });
    } else {
      router.push('/');
    }
  }, [router, searchParams]);

  return null;
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<p className="p-6 text-gray-400 text-center">Procesando inicio de sesión...</p>}>
      <CallbackInner />
    </Suspense>
  );
}
