import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "topdek"

CATEGORIES = ["placa-mae", "placa-de-video", "processador", "memoria-ram", "ssd",
              "fonte", "gabinete", "notebook-e-pc-mini", "monitor", "mouse-e-teclado",
              "cooler", "headset", "cadeira-gamer", "destaques", "pc-montado",
              "gabinete-gamer", "teclado-mecanico", "water-cooler", "caixa-de-som",
              "roteador", "webcam", "hd-externo", "pen-drive", "cabo-conector",
              "impressora", "cadeira-escritorio"]

def scrape(query: str = "") -> list[dict]:
    products = []
    seen = set()

    for cat in CATEGORIES:
        url = f"https://www.topdekinformatica.com.br/categoria/{cat}"
        try:
            soup = fetch_html(url, timeout=60)
            if not soup or not soup.title:
                continue
        except Exception:
            continue

        found = 0
        for card in soup.select("[class*=product]"):
            title_el = card.select_one(".product-title, [class*=title]")
            if not title_el:
                continue
            name = title_el.get_text(strip=True)
            if not name or len(name) < 4:
                continue

            price_el = card.select_one(".product-price, [class*=price], .preco")
            img_el = card.select_one("img")
            link_el = card.select_one("a[href*='/produto/']") or card.select_one("a[href*='/product/']") or card.select_one("a")

            href = link_el.get("href", "") if link_el else ""
            if href and not href.startswith("http"):
                href = "https://www.topdekinformatica.com.br" + (href if href.startswith("/") else "/" + href)

            if href in seen:
                continue
            seen.add(href)

            img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
            if img_src and not img_src.startswith("http"):
                img_src = "https:" + img_src if img_src.startswith("//") else ""

            ext_id_match = re.search(r"/(\d+)/?", href) or re.search(r"-p-(\d+)", href) or re.search(r"id=(\d+)", href)
            external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

            ext_id = external_id + "_" + re.sub(r"[^a-z0-9]", "", name.lower().split()[-1][:10]) if external_id.isdigit() and external_id else external_id

            products.append({
                "name": name,
                "price": parse_price(price_el.get_text(strip=True) if price_el else None),
                "image_url": img_src or None,
                "source_url": href,
                "external_id": ext_id,
                "store_origin": STORE_ID,
            })
            found += 1

        print(f"  topdek '{cat}': {found} productos")
        polite_delay(0.3, 0.8)

    return products
