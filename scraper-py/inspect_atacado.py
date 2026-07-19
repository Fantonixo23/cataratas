import sys, re
sys.stdout.reconfigure(encoding='utf-8')

from common import fetch_html

soup = fetch_html("https://atacadoconnect.com/categoria/smartphones")

# Buscar todas las clases que podrían ser productos
for el in soup.find_all(class_=True):
    classes = " ".join(el.get("class", []))
    if any(k in classes.lower() for k in ["product", "item", "card", "produto", "prod"]):
        print(f"<{el.name} class='{classes[:80]}'>")
        # Get first child text
        txt = el.get_text(strip=True)[:60] if el.get_text(strip=True) else ""
        if txt:
            print(f"  text: {txt}")

# Also try to find product links / images
links = soup.find_all("a", href=re.compile(r"/produto/"))[:3]
print(f"\nLinks /produto/: {len(links)} encontrados")
for a in links[:3]:
    print(f"  {a.get('href')} → {a.get_text(strip=True)[:50]}")

# Find product names
names = soup.find_all(["h1", "h2", "h3", "h4"], string=re.compile(r"Smartphone|iPhone|Celular", re.I))[:5]
print(f"\nTítulos con Smartphone/iPhone: {len(names)}")
for n in names:
    print(f"  <{n.name}> {n.get_text(strip=True)[:60]}")
