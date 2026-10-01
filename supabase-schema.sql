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

-- brand_slug(brand): normaliza el texto libre de la columna brand a un slug
-- utilizable en la URL /marca/[slug]. El translate() cubre las vocales
-- acentuadas y la enye, que si no se limpian abortan el regexp.
-- IMMUTABLE es obligatorio: la Generated Column de abajo lo exige.
CREATE OR REPLACE FUNCTION brand_slug(brand TEXT)
RETURNS TEXT
LANGUAGE sql IMMUTABLE AS $$
  SELECT NULLIF(
    trim(both '-' FROM
      regexp_replace(
        lower(translate(brand, 'áàäâãéèëêíìïîóòöôõúùüûñç', 'aaaaaeeeeiiiiooooouuuuunc')),
        '[^a-z0-9]+', '-', 'g'
      )
    ), ''
  );
$$;

-- Slug materializado para poder filtrar e indexar por marca sin un seq scan
-- sobre ~24k filas. Se recalcula solo cuando el scraper actualiza products.brand.
ALTER TABLE products
  ADD COLUMN IF NOT EXISTS brand_slug TEXT
  GENERATED ALWAYS AS (brand_slug(brand)) STORED;

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

-- Marcas: la seccion /marcas cuenta productos por brand, y /marca/[slug] filtra
-- por brand normalizado. La trigram acelera la busqueda dentro de la marca.
CREATE INDEX IF NOT EXISTS idx_products_brand       ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_brand_trgm  ON products USING GIN(brand gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_products_brand_slug  ON products(brand_slug);

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

-- Eventos de interes (clicks, vistas, favoritos, carrito, WhatsApp).
-- Es la unica tabla que escribe el usuario final, y solo a traves de
-- POST /api/track. El peso ya vemene calculado desde el cliente segun el tipo
-- de evento: mirar no es lo mismo que agregar al carrito.
CREATE TABLE IF NOT EXISTS product_events (
  id BIGSERIAL PRIMARY KEY,
  product_external_id TEXT NOT NULL,
  store_origin TEXT NOT NULL,
  event_type TEXT NOT NULL CHECK (event_type IN ('view', 'click', 'favorite', 'cart', 'whatsapp')),
  weight INT NOT NULL DEFAULT 1,
  visitor_id TEXT,
  user_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE product_events ENABLE ROW LEVEL SECURITY;

CREATE INDEX IF NOT EXISTS idx_product_events_created_at ON product_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_product_events_product      ON product_events(store_origin, product_external_id);

-- trending_products(p_limit, p_days)
-- Devuelve los productos mas solicitados con decaimiento exponencial: un click
-- de hace una semana vale la mitad que uno de hoy, asi el carrusel de la home
-- se mueve solo. Half-life de 7 dias.
CREATE OR REPLACE FUNCTION trending_products(
  p_limit INT DEFAULT 12,
  p_days  INT DEFAULT 30
)
RETURNS TABLE (
  store_origin TEXT,
  product_external_id TEXT,
  score NUMERIC,
  events BIGINT
)
LANGUAGE sql STABLE AS $$
  SELECT
    pe.store_origin,
    pe.product_external_id,
    ROUND(SUM(
      pe.weight * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - pe.created_at))::numeric / 604800.0)
    )::numeric, 3) AS score,
    COUNT(*) AS events
  FROM product_events pe
  WHERE pe.created_at > NOW() - make_interval(days => p_days)
  GROUP BY pe.store_origin, pe.product_external_id
  ORDER BY 3 DESC
  LIMIT p_limit;
$$;

-- brand_counts(p_min, p_limit)
-- Marcas con al menos p_min productos en catalogo, que es el corte que usa la
-- pagina /marcas para no llenar la grilla de marcas de un solo producto.
-- El denylist descarta etiquetas que las tiendas ponen en la columna brand
-- pero que no son marcas (ej. "Original", "Generico").
CREATE OR REPLACE FUNCTION brand_counts(
  p_min   INT DEFAULT 3,
  p_limit INT DEFAULT 200
)
RETURNS TABLE (
  brand TEXT,
  slug TEXT,
  products BIGINT
)
LANGUAGE sql STABLE AS $$
  SELECT
    p.brand,
    brand_slug(p.brand) AS slug,
    COUNT(*) AS products
  FROM products p
  WHERE p.available = true
    AND p.brand IS NOT NULL
    AND length(trim(p.brand)) BETWEEN 2 AND 40
    AND lower(trim(p.brand)) <> ALL (ARRAY[
      'original', 'generico', 'genuino', 'sin marca', 's/m', 'no aplica',
      'n/a', 'otro', 'otros', 'mixto', 'varios', 'null', '-'
    ])
  GROUP BY p.brand
  HAVING COUNT(*) >= p_min
  ORDER BY 3 DESC, 1 ASC
  LIMIT p_limit;
$$;
