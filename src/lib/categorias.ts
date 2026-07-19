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
];

export function getCategoriaBySlug(slug: string): Categoria | undefined {
  return CATEGORIAS.find((c) => c.slug === slug);
}

export function getCategoriaByName(name: string): Categoria | undefined {
  return CATEGORIAS.find((c) => c.name === name);
}
