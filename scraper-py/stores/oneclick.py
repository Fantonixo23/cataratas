import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "oneclick"

CATEGORIES = [
    "informatica", "informatica/computadores", "informatica/acessorios-informatica", "informatica/tablet",
    "celulares", "celulares/smartphones", "celulares/acessorios-celular",
    "eletronicos", "eletronicos/audio-video", "eletronicos/fone-de-ouvido", "eletronicos/smartwatches",
    "eletronicos/relogios", "eletronicos/drones",
    "camaras", "camaras/camara-fotografica", "camaras/filmadoras",
    "games", "games/consoles", "games/juegos", "games/acessorios-games",
    "saude", "saude/cabelo", "saude/higiene",
    "pecas-de-reposicao",
]

def scrape(query: str = "") -> list[dict]:
    products = []
    seen = set()

    for cat in CATEGORIES:
        url = f"https://oneclick.com.py/categoria/{cat}"
        try:
            soup = fetch_html(url, timeout=20)
        except Exception:
            continue

        for a in soup.select("a[href*='/produto/cod-']"):
            href = a.get("href", "")
            if not href or href in seen:
                continue
            seen.add(href)

            name = a.get_text(strip=True)
            img = a.select_one("img")
            img_src = img.get("src") or img.get("data-src") or "" if img else ""
            parent = a.find_parent()
            price_el = parent.select_one("[class*=price], .preco, .valor, [class*=preco]") if parent else None

            if not name and not img_src:
                continue
            if not name:
                name = img.get("alt", "") if img else ""

            if not href.startswith("http"):
                href = "https://oneclick.com.py" + href

            if img_src and not img_src.startswith("http"):
                img_src = "https:" + img_src if img_src.startswith("//") else ""

            ext_id_match = re.search(r"/cod-(\d+)", href) or re.search(r"-(\d+)-desc-", href)
            external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

            products.append({
                "name": name.strip() if name else "",
                "price": parse_price(price_el.get_text(strip=True) if price_el else None),
                "image_url": img_src or None,
                "source_url": href,
                "external_id": external_id,
                "store_origin": STORE_ID,
            })

        polite_delay(0.5, 1.5)

    return products
