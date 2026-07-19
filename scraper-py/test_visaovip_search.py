import sys, re
sys.stdout.reconfigure(encoding='utf-8')

from common import fetch_html

# Probar diferentes formas de buscar en Visaovip
urls = [
    ("busca iphone", "https://visaovip.com/es/busca/iphone"),
    ("busca?q=iphone", "https://visaovip.com/es/busca?q=iphone"),
    ("categoria celulares", "https://visaovip.com/es/busca/categoria/celulares/"),
    ("promocoes", "https://visaovip.com/es/busca/promocoes/"),
    ("categoria notebook", "https://visaovip.com/es/busca/categoria/notebook-y-computadoras/20/"),
]

for label, url in urls:
    try:
        soup = fetch_html(url, timeout=10)
        title = soup.title.string if soup.title else "N/A"
        links = soup.select("a[href*='/es/prod/']")
        print(f"{label:35s} → status OK | {len(links)} links | {title[:50]}")
    except Exception as e:
        print(f"{label:35s} → ERROR: {e}")
