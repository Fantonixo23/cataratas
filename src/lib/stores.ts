export interface StoreInfo {
  id: string;
  name: string;
  location: string;
  city: string;
  country: string;
  url: string;
}

// .com.py → Ciudad del Este, Paraguay
export const STORES: Record<string, StoreInfo> = {
  cellshop: {
    id: "cellshop",
    name: "Cellshop",
    location: "Microcentro, Ciudad del Este",
    city: "Ciudad del Este",
    country: "Paraguay",
    url: "https://www.cellshop.com.py",
  },
  visaovip: {
    id: "visaovip",
    name: "Visão VIP",
    location: "Edificio New York, Microcentro, Ciudad del Este",
    city: "Ciudad del Este",
    country: "Paraguay",
    url: "https://www.visaovip.com.py",
  },
  nissei: {
    id: "nissei",
    name: "Nissei",
    location: "Microcentro, Ciudad del Este",
    city: "Ciudad del Este",
    country: "Paraguay",
    url: "https://nissei.com",
  },
  megaelectronicos: {
    id: "megaelectronicos",
    name: "Mega Electrónicos",
    location: "Microcentro, Ciudad del Este",
    city: "Ciudad del Este",
    country: "Paraguay",
    url: "https://megaelectronicos.com.py",
  },
  shoppingchina: {
    id: "shoppingchina",
    name: "Shopping China",
    location: "Microcentro, Ciudad del Este",
    city: "Ciudad del Este",
    country: "Paraguay",
    url: "https://shoppingchina.com.py",
  },
  bristol: {
    id: "bristol",
    name: "Bristol",
    location: "Microcentro, Ciudad del Este",
    city: "Ciudad del Este",
    country: "Paraguay",
    url: "https://bristol.com.py",
  },
  guaranielectro: {
    id: "guaranielectro",
    name: "Guaraní Electro",
    location: "Microcentro, Ciudad del Este",
    city: "Ciudad del Este",
    country: "Paraguay",
    url: "https://guaranielectro.com.py",
  },
  tiendamovil: {
    id: "tiendamovil",
    name: "Tienda Móvil",
    location: "Microcentro, Ciudad del Este",
    city: "Ciudad del Este",
    country: "Paraguay",
    url: "https://tiendamovil.com.py",
  },
  electronica: {
    id: "electronica",
    name: "Electrónica",
    location: "Microcentro, Ciudad del Este",
    city: "Ciudad del Este",
    country: "Paraguay",
    url: "https://electronica.com.py",
  },
  electropar: {
    id: "electropar",
    name: "Electropar",
    location: "Microcentro, Ciudad del Este",
    city: "Ciudad del Este",
    country: "Paraguay",
    url: "https://electropar.com.py",
  },
  casarica: {
    id: "casarica",
    name: "Casa Rica",
    location: "Shopping Paraná, Ciudad del Este y sucursales a nivel nacional",
    city: "Ciudad del Este (y otras)",
    country: "Paraguay",
    url: "https://www.casarica.com.py",
  },
  intershop: {
    id: "intershop",
    name: "Intershop",
    location: "Microcentro, Ciudad del Este",
    city: "Ciudad del Este",
    country: "Paraguay",
    url: "https://intershop.com.py",
  },
};

export function getStoreInfo(storeId: string): StoreInfo | undefined {
  return STORES[storeId];
}

export function formatStoreOrigin(storeId: string): string {
  const info = STORES[storeId];
  return info ? `${info.name} - ${info.city}, ${info.country}` : storeId;
}
