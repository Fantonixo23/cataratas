import urllib.request, re
from bs4 import BeautifulSoup

for name, url in [("casarica", "https://www.casarica.com.py/catalogo?q=celular"), ("electropar", "https://www.electropar.com.py/catalogo?store=tienda&q=celular")]:
    print(f"\n=== {name} ===")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    imgs = soup.select("img")
    print(f"Total images: {len(imgs)}")
    for img in imgs:
        src = img.get("src") or ""
        alt = img.get("alt", "")[:30]
        # Only show image-looking URLs
        if any(ext in src.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            print(f"  {src[:100]}")
