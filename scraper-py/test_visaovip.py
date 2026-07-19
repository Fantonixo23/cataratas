import sys, re
sys.stdout.reconfigure(encoding='utf-8')

from common import fetch_html

urls = [
    ("home", "https://visaovip.com/es/"),
    ("busca iphone", "https://visaovip.com/es/busca?q=iphone"),
    ("categoria smartphone", "https://visaovip.com/es/busca/categoria/smartphone/1"),
    ("busca iphone 2", "https://visaovip.com/es/busca/iphone"),
]

for label, url in urls:
    try:
        soup = fetch_html(url, timeout=10)
        title = soup.title.string if soup.title else "N/A"
        # Try to find product containers
        for cls in ["product", "item", "card", "prod", "product-item", "box-produto", "produto-box"]:
            items = soup.select(f".{cls}")
            if items:
                print(f"{label:30s} → {len(items)} .{cls} | {title[:50]}")
                break
        else:
            # Check for other patterns
            imgs = soup.find_all("img", src=re.compile(r"visaovip\.com/img/prod"))
            links = soup.find_all("a", href=re.compile(r"/es/prod/"))
            print(f"{label:30s} → sin contenedor conocido | imgs:{len(imgs)} links-prod:{len(links)} | {title[:50]}")
    except Exception as e:
        print(f"{label:30s} → ERROR: {e}")
