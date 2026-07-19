import { Product } from '@/lib/types';

export default function ProductCard({ product }: { product: Product }) {
  const whatsappLink = product.whatsapp_message || (
    `https://wa.me/5959XXXXXXXX?text=${encodeURIComponent(
      `Hola! quisiera saber sobre "${product.name}" y su precio, muchas gracias :D`
    )}`
  );

  return (
    <div className="border rounded-lg p-3 flex flex-col">
      {product.image_url && (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={product.image_url} alt={product.name} className="w-full h-32 object-contain" />
      )}
      <h3 className="text-sm font-medium mt-2 line-clamp-2">{product.name}</h3>

      <a
        href={whatsappLink}
        target="_blank"
        rel="noopener noreferrer"
        className="block text-center bg-green-600 hover:bg-green-700 text-white text-base font-semibold rounded-lg py-3 mt-3 transition-colors"
      >
        Consultar precio por WhatsApp
      </a>
    </div>
  );
}
