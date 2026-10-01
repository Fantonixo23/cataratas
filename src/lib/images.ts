/**
 * Imagenes de fondo del sitio.
 *
 * Cada valor es una ruta dentro de /public. Si el archivo no existe todavia,
 * el componente que lo usa cae al fondo con gradiente + patron SVG, asi que el
 * diseno nunca se ve roto. Para activar una foto, subi el archivo a /public/img
 * con el nombre de aqui y recargar.
 *
 * Formatos recomendados: .webp o .jpg, entre 1600px y 2400px de ancho.
 */
export const IMAGES = {
  /** Fondo del bloque "Quienes somos": panoramica de Ciudad del Este. */
  ciudadDelEste: '/img/ciudad-del-este.webp',

  /** Cielo del hero, con overlay oscuro para que resalte el texto. */
  heroEcommerce: '/img/hero-ecommerce.webp',

  /** Franja decorativa: personas elegiendo productos en un local. */
  franjaPersonas: '/img/personas-comprando.webp',

  /** Franja decorativa: packaging y envio de paquetes. */
  franjaEnvios: '/img/envio-paquetes.webp',

  /** Franja decorativa: Cellshop / toldos de la zona comercial. */
  franjaComercio: '/img/zona-comercial.webp',
} as const;

export type ImageKey = keyof typeof IMAGES;
