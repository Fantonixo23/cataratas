export interface Product {
  id?: string;
  external_id?: string;
  name: string;
  price?: number | null;
  image_url: string | null;
  source_url: string;
  store_origin: string;
  whatsapp_message?: string;
}
