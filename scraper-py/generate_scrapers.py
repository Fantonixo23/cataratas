import os, shutil

# Template for query-based scrapers
TEMPLATE_QUERY = '''import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "{store_id}"

def scrape(query: str) -> list[dict]:
    url = "{url_pattern}"
    try:
        soup = fetch_html(url)
    except Exception:
        return []

    products = []
    for card in soup.select("{card_selector}"):
        name_el = card.select_one("{name_selector}")
        img_el = card.select_one("img")
        price_el = card.select_one("{price_selector}")

        if not name_el:
            name_el = card.select_one("a")
            if not name_el:
                continue

        name = name_el.get_text(strip=True)
        if not name or len(name) < 4:
            continue

        href = name_el.get("href", "")
        if href and not href.startswith("http"):
            href = "{base_url}" + (href if href.startswith("/") else "/" + href)

        img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
        if img_src and not img_src.startswith("http"):
            img_src = "https:" + img_src if img_src.startswith("//") else ""

        ext_id_match = re.search(r"{id_regex}", href)
        external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

        products.append({{
            "name": name,
            "price": parse_price(price_el.get_text(strip=True) if price_el else None),
            "image_url": img_src or None,
            "source_url": href,
            "external_id": external_id,
            "store_origin": STORE_ID,
        }})

    polite_delay()
    return products
'''

SCRAPERS = []

# 1. SHOPPING CHINA (fix existing)
SCRAPERS.append({
    "filename": "shoppingchina.py",
    "content": '''import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "shoppingchina"

def scrape(query: str) -> list[dict]:
    url = f"https://www.shoppingchina.com.py/site/search?query={query}"
    try:
        soup = fetch_html(url)
    except Exception:
        return []

    products = []
    for card in soup.select(".product-item, .card.product-item, [class*=product-item]"):
        name_el = card.select_one("h3 a, h4 a, [class*=product-name] a, a[class*=product], .card-title a")
        img_el = card.select_one("img")
        price_el = card.select_one("[class*=price], .precio, [class*=preco], .card-text")

        if not name_el:
            continue

        name = name_el.get_text(strip=True)
        if not name or len(name) < 4:
            continue

        href = name_el.get("href", "")
        if href and not href.startswith("http"):
            href = "https://www.shoppingchina.com.py" + (href if href.startswith("/") else "/" + href)

        img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
        if img_src and not img_src.startswith("http"):
            img_src = "https:" + img_src if img_src.startswith("//") else ""

        ext_id_match = re.search(r"/prod/(\d+)", href) or re.search(r"id=(\d+)", href) or re.search(r"/(\d+)/?", href)
        external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

        products.append({
            "name": name,
            "price": parse_price(price_el.get_text(strip=True) if price_el else None),
            "image_url": img_src or None,
            "source_url": href,
            "external_id": external_id,
            "store_origin": STORE_ID,
        })

    polite_delay()
    return products
'''
})

# 2. NISSEI (fix)
SCRAPERS.append({
    "filename": "nissei.py",
    "content": '''import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "nissei"

def scrape(query: str) -> list[dict]:
    for url in [
        f"https://nissei.com/py/{query}?q={query}&map=ft",
        f"https://nissei.com.py/py/{query}",
        f"https://nissei.com.py/{query}",
    ]:
        try:
            soup = fetch_html(url)
            break
        except Exception:
            continue
    else:
        return []

    products = []
    for card in soup.select("article, .product-item, [class*=product], .card, .item, .produto-item, [class*=shelf], li[class]"):
        name_el = card.select_one("a[title], .product-name, h2, h3 a, [class*=name] a, .info-card a, a[href*='/py/']")
        link_el = card.select_one("a[href*='/py/']") or card.select_one("a[href*='nissei']") or card.select_one("a")
        img_el = card.select_one("img")
        price_el = card.select_one("[class*=price], .precio, [class*=preco], .valor")

        if not name_el:
            continue

        name = name_el.get_text(strip=True)
        if not name or len(name) < 5:
            continue

        href = link_el.get("href", "") if link_el else ""
        if href and not href.startswith("http"):
            href = "https://nissei.com" + (href if href.startswith("/") else "/py/" + href)

        img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
        if img_src and not img_src.startswith("http"):
            img_src = "https:" + img_src if img_src.startswith("//") else ""

        ext_id_match = re.search(r"/p/([^/]+)", href) or re.search(r"-p-(\\\\d+)", href) or re.search(r"/(\\\\d+)/?", href)
        external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

        products.append({
            "name": name,
            "price": parse_price(price_el.get_text(strip=True) if price_el else None),
            "image_url": img_src or None,
            "source_url": href,
            "external_id": external_id,
            "store_origin": STORE_ID,
        })

    polite_delay()
    return products
'''
})

# 3. MOBILEZONE
SCRAPERS.append({
    "filename": "mobilezone.py",
    "content": '''import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "mobilezone"

def scrape(query: str) -> list[dict]:
    for url in [
        f"https://www.mobilezone.com.py/busca?q={query}",
        f"https://www.mobilezone.com.py/",
    ]:
        try:
            soup = fetch_html(url)
            if soup.title and soup.title.string and "Mobile" in soup.title.string:
                break
        except Exception:
            continue
    else:
        return []

    products = []
    for card in soup.select("[class*=product], [class*=item], .card, article, [class*=produto], .grid-item, li[class]"):
        name_el = card.select_one("h2 a, h3 a, h4 a, [class*=name] a, [class*=title] a, a[href*='/produto/'], a[href*='/product/']")
        img_el = card.select_one("img")
        price_el = card.select_one("[class*=price], .precio, [class*=preco], .valor")

        if not name_el:
            continue

        name = name_el.get_text(strip=True)
        if not name or len(name) < 4:
            continue

        href = name_el.get("href", "")
        if href and not href.startswith("http"):
            href = "https://www.mobilezone.com.py" + (href if href.startswith("/") else "/" + href)

        img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
        if img_src and not img_src.startswith("http"):
            img_src = "https:" + img_src if img_src.startswith("//") else ""

        ext_id_match = re.search(r"/(\\\\d+)/?", href) or re.search(r"id=(\\\\d+)", href) or re.search(r"-p-(\\\\d+)", href)
        external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

        products.append({
            "name": name,
            "price": parse_price(price_el.get_text(strip=True) if price_el else None),
            "image_url": img_src or None,
            "source_url": href,
            "external_id": external_id,
            "store_origin": STORE_ID,
        })

    polite_delay()
    return products
'''
})

# 4. ELEGANCIA COMPANY (perfumes)
SCRAPERS.append({
    "filename": "elegancia.py",
    "content": '''import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "elegancia"

def scrape(query: str) -> list[dict]:
    url = f"https://www.eleganciacompany.com/productos?menu_id=perfumes"
    try:
        soup = fetch_html(url)
    except Exception:
        return []

    products = []
    seen_hrefs = set()

    # Products are listed as direct links on the page
    for a in soup.select("a[href*='/productos/']"):
        href = a.get("href", "")
        if not href or href in seen_hrefs:
            continue
        seen_hrefs.add(href)
        
        img = a.select_one("img")
        name = a.get_text(strip=True) or (img.get("alt", "") if img else "")
        if not name or len(name) < 3:
            continue
        if name in ("", "Codigo:", "Codigo"):
            continue

        if not href.startswith("http"):
            href = "https://www.eleganciacompany.com" + href

        img_src = img.get("src") or img.get("data-src") or "" if img else ""
        if img_src and not img_src.startswith("http"):
            img_src = "https:" + img_src if img_src.startswith("//") else ""

        ext_id_match = re.search(r"/(\\\\d+)$", href)
        external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

        products.append({
            "name": name,
            "price": None,
            "image_url": img_src or None,
            "source_url": href,
            "external_id": external_id,
            "store_origin": STORE_ID,
        })

    polite_delay()
    return products
'''
})

# 5. ATACADO CONNECT
SCRAPERS.append({
    "filename": "atacadoconnect.py",
    "content": '''import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "atacadoconnect"

def scrape(query: str) -> list[dict]:
    for url in [
        f"https://www.atacadoconnect.com/busca?q={query}",
        f"https://www.atacadoconnect.com/categoria/{query}",
        f"https://www.atacadoconnect.com/",
    ]:
        try:
            soup = fetch_html(url)
            break
        except Exception:
            continue
    else:
        return []

    products = []
    for card in soup.select("[class*=product], [class*=item], .card, article, [class*=produto], .grid-item, li[class]"):
        name_el = card.select_one("h2 a, h3 a, h4 a, [class*=name] a, [class*=title] a, a[href*='/produto/'], a[href*='/product/']")
        img_el = card.select_one("img")
        price_el = card.select_one("[class*=price], .precio, [class*=preco], .valor, [class*=preco]")

        if not name_el:
            continue

        name = name_el.get_text(strip=True)
        if not name or len(name) < 4:
            continue

        href = name_el.get("href", "")
        if href and not href.startswith("http"):
            href = "https://www.atacadoconnect.com" + (href if href.startswith("/") else "/" + href)

        img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
        if img_src and not img_src.startswith("http"):
            img_src = "https:" + img_src if img_src.startswith("//") else ""

        ext_id_match = re.search(r"/(\\\\d+)/?", href) or re.search(r"id=(\\\\d+)", href)
        external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

        products.append({
            "name": name,
            "price": parse_price(price_el.get_text(strip=True) if price_el else None),
            "image_url": img_src or None,
            "source_url": href,
            "external_id": external_id,
            "store_origin": STORE_ID,
        })

    polite_delay()
    return products
'''
})

# 6. NEW ZONE
SCRAPERS.append({
    "filename": "newzone.py",
    "content": '''import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "newzone"

def scrape(query: str) -> list[dict]:
    for url in [
        f"https://newzone.com.py/busca?q={query}",
        f"https://newzone.com.py/",
    ]:
        try:
            soup = fetch_html(url)
            break
        except Exception:
            continue
    else:
        return []

    products = []
    seen = set()

    # NewZone lists products as links with /producto/ID/name
    for a in soup.select("a[href*='/producto/']"):
        href = a.get("href", "")
        if not href or href in seen:
            continue
        seen.add(href)

        name = a.get_text(strip=True)
        img = a.select_one("img")
        img_src = img.get("src") or img.get("data-src") or "" if img else ""

        if not name and not img_src:
            continue

        if not name:
            name = img.get("alt", "") if img else ""

        if not href.startswith("http"):
            href = "https://newzone.com.py" + href

        if img_src and not img_src.startswith("http"):
            img_src = "https:" + img_src if img_src.startswith("//") else ""

        ext_id_match = re.search(r"/producto/(\\\\d+)", href)
        external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

        products.append({
            "name": name.strip() if name else "",
            "price": None,
            "image_url": img_src or None,
            "source_url": href,
            "external_id": external_id,
            "store_origin": STORE_ID,
        })

    polite_delay()
    return products
'''
})

# 7. ONE CLICK
SCRAPERS.append({
    "filename": "oneclick.py",
    "content": '''import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "oneclick"

def scrape(query: str) -> list[dict]:
    for url in [
        f"https://oneclick.com.py/busca/{query}",
        f"https://oneclick.com.py/categoria/informatica",
        f"https://oneclick.com.py/categoria/celulares/smartphones",
        f"https://oneclick.com.py/categoria/eletronicos",
        f"https://oneclick.com.py/",
    ]:
        try:
            soup = fetch_html(url)
            break
        except Exception:
            continue
    else:
        return []

    products = []
    seen = set()

    for a in soup.select("a[href*='/produto/cod-']"):
        href = a.get("href", "")
        if not href or href in seen:
            continue
        seen.add(href)

        name = a.get_text(strip=True)
        img = a.select_one("img")
        img_src = img.get("src") or img.get("data-src") or "" if img else ""
        price_el = a.find_parent().select_one("[class*=price], .preco, .valor") if a.find_parent() else None

        if not name and not img_src:
            continue
        if not name:
            name = img.get("alt", "") if img else ""

        if not href.startswith("http"):
            href = "https://oneclick.com.py" + href

        if img_src and not img_src.startswith("http"):
            img_src = "https:" + img_src if img_src.startswith("//") else ""

        ext_id_match = re.search(r"/cod-(\\\\d+)", href) or re.search(r"/(\\\\d+)-desc-", href)
        external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

        products.append({
            "name": name.strip() if name else "",
            "price": parse_price(price_el.get_text(strip=True) if price_el else None),
            "image_url": img_src or None,
            "source_url": href,
            "external_id": external_id,
            "store_origin": STORE_ID,
        })

    polite_delay()
    return products
'''
})

# 8. MADRID CENTER
SCRAPERS.append({
    "filename": "madridcenter.py",
    "content": '''import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "madridcenter"

def scrape(query: str) -> list[dict]:
    for url in [
        f"https://madridcenterimportados.com/busca?q={query}",
        f"https://madridcenterimportados.com/",
        f"https://madridcenter.com.py/",
    ]:
        try:
            soup = fetch_html(url)
            break
        except Exception:
            continue
    else:
        return []

    products = []
    for card in soup.select("[class*=product], [class*=item], .card, article, [class*=produto], li[class]"):
        name_el = card.select_one("h2 a, h3 a, h4 a, [class*=name] a, [class*=title] a, a[href*='/produto/'], a[href*='/product/']")
        img_el = card.select_one("img")
        price_el = card.select_one("[class*=price], .precio, [class*=preco], .valor")

        if not name_el:
            continue

        name = name_el.get_text(strip=True)
        if not name or len(name) < 4:
            continue

        href = name_el.get("href", "")
        if href and not href.startswith("http"):
            href = "https://madridcenterimportados.com" + (href if href.startswith("/") else "/" + href)

        img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
        if img_src and not img_src.startswith("http"):
            img_src = "https:" + img_src if img_src.startswith("//") else ""

        ext_id_match = re.search(r"/(\\\\d+)/?", href) or re.search(r"id=(\\\\d+)", href)
        external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

        products.append({
            "name": name,
            "price": parse_price(price_el.get_text(strip=True) if price_el else None),
            "image_url": img_src or None,
            "source_url": href,
            "external_id": external_id,
            "store_origin": STORE_ID,
        })

    polite_delay()
    return products
'''
})

# 9. TOPDEK INFORMATICA
SCRAPERS.append({
    "filename": "topdek.py",
    "content": '''import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "topdek"

CATEGORIES = ["placa-mae", "placa-de-video", "processador", "memoria-ram", "ssd",
              "fonte", "gabinete", "notebook-e-pc-mini", "monitor", "mouse-e-teclado",
              "cooler", "headset", "cadeira-gamer", "destaques"]

def scrape(query: str) -> list[dict]:
    products = []
    # Try specific search first, then scrape categories
    for url in [
        f"https://www.topdekinformatica.com.br/busca?q={query}",
    ] + [f"https://www.topdekinformatica.com.br/categoria/{cat}" for cat in CATEGORIES]:
        try:
            soup = fetch_html(url, timeout=20)
        except Exception:
            continue

        for card in soup.select("[class*=product]"):
            name_el = card.select_one(".product-title, [class*=title], h2, h3")
            price_el = card.select_one(".product-price, [class*=price], .preco")
            img_el = card.select_one("img")
            link_el = card.select_one("a[href]")

            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 4:
                continue

            href = link_el.get("href", "") if link_el else ""
            if href and not href.startswith("http"):
                href = "https://www.topdekinformatica.com.br" + (href if href.startswith("/") else "/" + href)

            img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
            if img_src and not img_src.startswith("http"):
                img_src = "https:" + img_src if img_src.startswith("//") else ""

            ext_id_match = re.search(r"/(\\\\d+)/?", href) or re.search(r"-p-(\\\\d+)", href) or re.search(r"id=(\\\\d+)", href)
            external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

            ext_id = external_id + "_" + re.sub(r"[^a-z0-9]", "", name.lower().split()[-1][:10]) if external_id.isdigit() else external_id
            products.append({
                "name": name,
                "price": parse_price(price_el.get_text(strip=True) if price_el else None),
                "image_url": img_src or None,
                "source_url": href,
                "external_id": ext_id,
                "store_origin": STORE_ID,
            })

    polite_delay()
    return products
'''
})

# 10. AGATRES
SCRAPERS.append({
    "filename": "agatres.py",
    "content": '''import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "agatres"

def scrape(query: str) -> list[dict]:
    all_products = []
    
    # Agatres has paginated product pages
    page = 1
    max_pages = 10
    while page <= max_pages:
        url = f"https://agatres.co/es/productos/page/{page}/" if page > 1 else "https://agatres.co/es/productos/"
        try:
            soup = fetch_html(url, timeout=20)
        except Exception:
            break

        cards = soup.select(".product, [class*=product]")
        if len(cards) == 0:
            break

        for card in cards:
            name_el = card.select_one("h2 a, h3 a, .product-title a, .woocommerce-loop-product__title, .wd-entities-title a")
            price_el = card.select_one(".price, .amount, .preco, .woocommerce-Price-amount")
            img_el = card.select_one("img")
            link_el = card.select_one("a[href*='agatres']") or card.select_one("h2 a") or card.select_one("h3 a") or card.select_one("a")

            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 4:
                continue

            href = link_el.get("href", "") if link_el else ""
            if href and not href.startswith("http"):
                href = "https://agatres.co" + href

            img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
            if img_src and not img_src.startswith("http"):
                img_src = "https:" + img_src if img_src.startswith("//") else ""

            ext_id_match = re.search(r"/(\\\\d+)/?", href) or re.search(r"p=(\\\\d+)", href)
            external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

            all_products.append({
                "name": name,
                "price": parse_price(price_el.get_text(strip=True) if price_el else None),
                "image_url": img_src or None,
                "source_url": href,
                "external_id": external_id,
                "store_origin": STORE_ID,
            })

        page += 1
        polite_delay(0.5, 1.5)

    return all_products
'''
})

# 11. LIFE BEACH
SCRAPERS.append({
    "filename": "lifebeach.py",
    "content": '''import re
from common import fetch_html, parse_price, polite_delay

STORE_ID = "lifebeach"

CATEGORIES = ["beach-tennis", "roupas", "acessorios", "padel", "tenis"]

def scrape(query: str) -> list[dict]:
    products = []
    for cat in CATEGORIES:
        url = f"https://www.lifebeach.com.py/categoria/{cat}"
        try:
            soup = fetch_html(url)
        except Exception:
            continue

        for card in soup.select(".product, .product-wrap, [class*=product]"):
            name_el = card.select_one(".product-name, [class*=name], h2, h3, h4")
            price_el = card.select_one(".product-price, .price, .preco, [class*=price]")
            img_el = card.select_one("img")
            link_el = card.select_one("a[href*='/produto/']") or card.select_one("a[href*='/producto/']") or card.select_one(".product-name a") or card.select_one("a")

            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 3:
                continue

            href = link_el.get("href", "") if link_el else ""
            if href and not href.startswith("http"):
                href = "https://www.lifebeach.com.py" + (href if href.startswith("/") else "/" + href)

            img_src = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""
            if img_src and not img_src.startswith("http"):
                img_src = "https:" + img_src if img_src.startswith("//") else ""

            ext_id_match = re.search(r"/(\\\\d+)/?", href) or re.search(r"id=(\\\\d+)", href)
            external_id = ext_id_match.group(1) if ext_id_match else re.sub(r"[^a-zA-Z0-9]", "", name)[:20]

            products.append({
                "name": name,
                "price": parse_price(price_el.get_text(strip=True) if price_el else None),
                "image_url": img_src or None,
                "source_url": href,
                "external_id": external_id,
                "store_origin": STORE_ID,
            })

        polite_delay()
    return products
'''
})

# Write all files
os.makedirs("stores", exist_ok=True)
for s in SCRAPERS:
    path = os.path.join("stores", s["filename"])
    with open(path, "w", encoding="utf-8") as f:
        f.write(s["content"].lstrip())
    print(f"Written: {path}")
