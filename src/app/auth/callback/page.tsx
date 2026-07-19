'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';

export default function AuthCallbackPage() {
  const router = useRouter();

  useEffect(() => {
    const hash = window.location.hash;
    if (hash && hash.includes('access_token')) {
      supabase.auth
        .setSession({
          access_token: new URLSearchParams(hash.slice(1)).get('access_token') ?? '',
          refresh_token: new URLSearchParams(hash.slice(1)).get('refresh_token') ?? '',
        })
        .then(() => {
          window.location.href = '/';
        });
    } else {
      router.push('/');
    }
  }, [router]);

  return <p className="p-6 text-gray-400 text-center">Procesando inicio de sesión...</p>;
}
