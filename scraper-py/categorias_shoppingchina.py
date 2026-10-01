"""
Mapeo de categorias de Shopping China a las categorias canonicas de Catarata.

Las 26 categorias top-level de Shopping China se colapsan a las 13 definidas
en src/lib/categorias.ts, para que el frontend (CategorySection, que hace
.eq('category', categoria.name)) funcione sin cambios.

La categoria original de la tienda se conserva en store_category, y la
subcategoria en store_subcategory.
"""

STORE_ID = "shoppingchina"

# slug top-level de Shopping China -> slug canonico de src/lib/categorias.ts
SC_TO_CATEGORIA = {
    "informatica": "informatica-notebooks",
    "electronicos": "electronica-tvs",
    "camaras-digitales": "electronica-tvs",
    "casa-y-decoracion": "hogar-electrodomesticos",
    "electrodomesticos": "hogar-electrodomesticos",
    "deportes": "deportes-fitness",
    "camping": "deportes-fitness",
    "pesca": "deportes-fitness",
    "moto-racing": "deportes-fitness",
    "moda-accesorios": "moda-accesorios",
    "moda-adulto": "moda-accesorios",
    "moda-infantil": "moda-accesorios",
    "calzados": "moda-accesorios",
    "cosmeticos": "perfumes-cosmeticos",
    "perfumeria": "perfumes-cosmeticos",
    "salud-y-belleza": "perfumes-cosmeticos",
    "jugueteria": "juguetes-hobbies",
    "navidenos": "juguetes-hobbies",
    "material-escolar-y-musical": "juguetes-hobbies",
    "ferreteria": "herramientas",
    "comestibles": "alimentos-bebidas",
    "bebidas": "alimentos-bebidas",
    "tabacos": "alimentos-bebidas",
    "mundo-del-bebe": "otros",
    "pets-shop": "otros",
    "tunning": "otros",
}

# slug canonico -> (nombre, icono, descripcion, posicion)
CATEGORIAS = {
    "celulares-tablets": (
        "Celulares y Tablets",
        "📱",
        "Smartphones, tablets, iPads y accesorios",
        1,
    ),
    "informatica-notebooks": (
        "Informática y Notebooks",
        "💻",
        "Notebooks, PC, monitores, componentes y periféricos",
        2,
    ),
    "electronica-tvs": (
        "Electrónica y TVs",
        "📺",
        "Televisores, home theater, parlantes y audio",
        3,
    ),
    "videojuegos-consolas": (
        "Videojuegos y Consolas",
        "🎮",
        "PlayStation, Xbox, Nintendo, juegos y accesorios",
        4,
    ),
    "audio-accesorios": (
        "Audio y Accesorios",
        "🎧",
        "Auriculares, cargadores, cables y accesorios",
        5,
    ),
    "perfumes-cosmeticos": (
        "Perfumes y Cosméticos",
        "🧴",
        "Perfumes, maquillaje, cuidado personal",
        6,
    ),
    "deportes-fitness": (
        "Deportes y Fitness",
        "⚽",
        "Raquetas, beach tennis, bicicletas, camping",
        7,
    ),
    "hogar-electrodomesticos": (
        "Hogar y Electrodomésticos",
        "🏠",
        "Cocina, lavarropas, heladeras, aspiradoras",
        8,
    ),
    "moda-accesorios": (
        "Moda y Accesorios",
        "👕",
        "Zapatillas, camisas, pantalones, vestidos",
        9,
    ),
    "juguetes-hobbies": (
        "Juguetes y Hobbies",
        "🎲",
        "Juguetes, LEGO, bicicletas, peluches",
        10,
    ),
    "herramientas": (
        "Herramientas",
        "🔧",
        "Taladros, martillos, herramientas en general",
        11,
    ),
    "alimentos-bebidas": (
        "Alimentos y Bebidas",
        "🍕",
        "Snacks, bebidas, productos de almacén",
        12,
    ),
    "otros": ("Otros", "📦", "Productos sin categoría específica", 13),
}

SLUG_A_NOMBRE = {slug: data[0] for slug, data in CATEGORIAS.items()}


def slugify(text):
    """'Casa y decoración' -> 'casa-y-decoracion' (igual que las slugs del sitio)."""
    import unicodedata

    norm = unicodedata.normalize("NFD", text.lower())
    norm = "".join(c for c in norm if unicodedata.category(c) != "Mn")
    out = []
    for c in norm:
        out.append(c if c.isalnum() else "-")
    return "".join(out).strip("-").replace("--", "-")


def categorizar(breadcrumb):
    """
    Devuelve (nombre_canonico, store_category, store_subcategory).

    Usa el primer crumb (categoria top-level de la tienda). Si el slug no esta
    en el mapa, cae en 'Otros' sin romper nada.
    """
    crumbs = [c for c in (breadcrumb or []) if c and c.strip()]
    if not crumbs:
        return SLUG_A_NOMBRE["otros"], None, None

    top = crumbs[0]
    slug = slugify(top)
    canonico = SC_TO_CATEGORIA.get(slug)
    if not canonico:
        # intento por coincidencia parcial antes de rendirse
        for sc_slug, dest in SC_TO_CATEGORIA.items():
            if sc_slug in slug or slug in sc_slug:
                canonico = dest
                break
    if not canonico:
        return SLUG_A_NOMBRE["otros"], slug, crumbs[1] if len(crumbs) > 1 else None

    sub = crumbs[1] if len(crumbs) > 1 else None
    return SLUG_A_NOMBRE[canonico], slug, sub


def catalogo_rows():
    """Filas para sembrar la tabla categories."""
    rows = []
    for slug, (name, icon, desc, pos) in CATEGORIAS.items():
        rows.append(
            {"name": name, "slug": slug, "description": desc, "icon": icon, "position": pos}
        )
    return rows
