import { createClient } from '@supabase/supabase-js';
import Link from 'next/link';
import ProductCard from '@/components/ProductCard';
import TrendingCarousel from '@/components/TrendingCarousel';
import QuienesSomos from '@/components/QuienesSomos';
import BrandsStrip from '@/components/BrandsStrip';
import EcommerceStrip from '@/components/EcommerceStrip';
import CtaBackground from '@/components/CtaBackground';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export default async function Home() {
  const { data: products } = await supabase
    .from('products')
    .select('name, price, image_url, source_url, store_origin, external_id, category, brand')
    .order('created_at', { ascending: false })
    .limit(20);

  return (
    <div className="py-6 space-y-12">
      <TrendingCarousel />

      <div>
        <div className="flex items-end justify-between gap-4 mb-1">
          <div>
            <h1 className="text-2xl font-bold">Productos destacados</h1>
            <p className="text-gray-500 text-sm">
              Lo Ãºltimo que cargamos del catÃ¡logo de Ciudad del Este
            </p>
          </div>
          <Link href="/marcas" className="text-sm font-medium text-blue-600 hover:underline shrink-0">
            Comprar por marca â†’
          </Link>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {(products || []).map((p: any) => (
            <ProductCard
              key={`${p.store_origin}-${p.external_id}`}
              product={p}
              showCategory
            />
          ))}
        </div>
      </div>

      <EcommerceStrip />

      <BrandsStrip
        limit={18}
        min={3}
        title="Nuestras marcas"
        subtitle="Las marcas con mÃ¡s productos en el catÃ¡logo. EntrÃ¡ y encontrÃ¡ todo lo que tenÃ©s de esa marca."
      />

      <QuienesSomos />

      <CtaBackground />
    </div>
  );
}
