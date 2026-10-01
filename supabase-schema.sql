-- Catalogo principal de productos (scrapers escriben, web lee)
-- category: texto que coincide con src/lib/categorias.ts (13 categorias canonicas)
-- store_category / store_subcategory: categoria original de la tienda, sin mapear
CREATE TABLE IF NOT EXISTS products (
  id BIGSERIAL PRIMARY KEY,
  external_id TEXT NOT NULL,
  store_origin TEXT NOT NULL,
  name TEXT NOT NULL,
  price NUMERIC,
  currency TEXT,
  image_url TEXT,
  source_url TEXT,
  brand TEXT,
  category TEXT,
  store_category TEXT,
  store_subcategory TEXT,
  available BOOLEAN DEFAULT true,
  image_file TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(store_origin, external_id)
);

ALTER TABLE products ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "products are publicly readable" ON products;
CREATE POLICY "products are publicly readable" ON products FOR SELECT USING (true);

-- Catalogos (categorias canonicas que usa el frontend)
CREATE TABLE IF NOT EXISTS categories (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  slug TEXT NOT NULL UNIQUE,
  description TEXT,
  icon TEXT,
  position INT DEFAULT 0
);

ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "categories are publicly readable" ON categories;
CREATE POLICY "categories are publicly readable" ON categories FOR SELECT USING (true);

-- Indices: el buscador usa ilike '%q%' sobre name, que necesita trigram
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS idx_products_category    ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_created_at  ON products(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_products_store       ON products(store_origin);
CREATE INDEX IF NOT EXISTS idx_products_available   ON products(available);
CREATE INDEX IF NOT EXISTS idx_products_name_trgm   ON products USING GIN(name gin_trgm_ops);

-- Favoritos
CREATE TABLE IF NOT EXISTS favorites (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  product_external_id TEXT NOT NULL,
  product_name TEXT,
  product_image TEXT,
  product_price TEXT,
  store_origin TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, product_external_id)
);

ALTER TABLE favorites ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users can read own favorites"
  ON favorites FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "users can insert own favorites"
  ON favorites FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "users can delete own favorites"
  ON favorites FOR DELETE
  USING (auth.uid() = user_id);

-- Carrito
CREATE TABLE IF NOT EXISTS cart_items (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  product_external_id TEXT NOT NULL,
  product_name TEXT,
  product_image TEXT,
  product_price TEXT,
  store_origin TEXT,
  source_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE cart_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users can read own cart"
  ON cart_items FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "users can insert own cart"
  ON cart_items FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "users can delete own cart"
  ON cart_items FOR DELETE
  USING (auth.uid() = user_id);
