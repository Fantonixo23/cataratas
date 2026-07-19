import sys
sys.stdout.reconfigure(encoding='utf-8')

from common import fetch_html

# Probar diferentes URLs de Atacado Connect
urls = [
    ("home", "https://atacadoconnect.com/"),
    ("busca iphone", "https://atacadoconnect.com/busca?q=iphone"),
    ("categoria smartphones", "https://atacadoconnect.com/categoria/smartphones"),
]

for label, url in urls:
    try:
        soup = fetch_html(url, timeout=10)
        title = soup.title.string if soup.title else "N/A"
        # Buscar cualquier contenedor de producto
        for cls in ["product", "item", "card", "prod", "product-item"]:
            items = soup.select(f".{cls}")
            if items:
                print(f"{label:30s} → {len(items)} .{cls} | Title: {title[:60]}")
                break
        else:
            print(f"{label:30s} → sin productos | Title: {title[:60]}")
    except Exception as e:
        print(f"{label:30s} → ERROR: {e}")
