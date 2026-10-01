import type { Metadata } from 'next';
import { use } from 'react';
import BrandProducts from '@/components/BrandProducts';

export const metadata: Metadata = {
  title: 'Productos por marca — Fronterra',
  description: 'Todos los productos de una marca en Ciudad del Este, Paraguay.',
};

export default async function MarcaPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return <BrandProducts slug={slug} />;
}
