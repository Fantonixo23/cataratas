export interface Categoria {
  name: string;
  slug: string;
  description: string;
  icon?: string;
}

export const CATEGORIAS: Categoria[] = [
  {
    name: "Celulares y Tablets",
    slug: "celulares-tablets",
    description: "Smartphones, tablets, iPads y accesorios",
    icon: "📱",
  },
  {
    name: "Informática y Notebooks",
    slug: "informatica-notebooks",
    description: "Notebooks, PC, monitores, componentes y periféricos",
    icon: "💻",
  },
  {
    name: "Electrónica y TVs",
    slug: "electronica-tvs",
    description: "Televisores, home theater, parlantes y audio",
    icon: "📺",
  },
  {
    name: "Videojuegos y Consolas",
    slug: "videojuegos-consolas",
    description: "PlayStation, Xbox, Nintendo, juegos y accesorios",
    icon: "🎮",
  },
  {
    name: "Audio y Accesorios",
    slug: "audio-accesorios",
    description: "Auriculares, cargadores, cables y accesorios",
    icon: "🎧",
  },
  {
    name: "Perfumes y Cosméticos",
    slug: "perfumes-cosmeticos",
    description: "Perfumes, maquillaje, cuidado personal",
    icon: "🧴",
  },
  {
    name: "Deportes y Fitness",
    slug: "deportes-fitness",
    description: "Raquetas, beach tennis, bicicletas, camping",
    icon: "⚽",
  },
  {
    name: "Hogar y Electrodomésticos",
    slug: "hogar-electrodomesticos",
    description: "Cocina, lavarropas, heladeras, aspiradoras",
    icon: "🏠",
  },
  {
    name: "Moda y Accesorios",
    slug: "moda-accesorios",
    description: "Zapatillas, camisas, pantalones, vestidos",
    icon: "👕",
  },
  {
    name: "Juguetes y Hobbies",
    slug: "juguetes-hobbies",
    description: "Juguetes, LEGO, bicicletas, peluches",
    icon: "🎲",
  },
  {
    name: "Herramientas",
    slug: "herramientas",
    description: "Taladros, martillos, herramientas en general",
    icon: "🔧",
  },
  {
    name: "Alimentos y Bebidas",
    slug: "alimentos-bebidas",
    description: "Snacks, bebidas, productos de almacén",
    icon: "🍕",
  },
  {
    name: "Otros",
    slug: "otros",
    description: "Productos sin categoría específica",
    icon: "📦",
  },
];

export function getCategoriaBySlug(slug: string): Categoria | undefined {
  return CATEGORIAS.find((c) => c.slug === slug);
}

export function getCategoriaByName(name: string): Categoria | undefined {
  return CATEGORIAS.find((c) => c.name === name);
}
