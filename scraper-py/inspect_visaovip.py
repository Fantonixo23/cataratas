import sys, re
sys.stdout.reconfigure(encoding='utf-8')

from common import fetch_html

soup = fetch_html("https://visaovip.com/es/")

# Find all product links
links = soup.find_all("a", href=re.compile(r"/es/prod/"))
print(f"Links /es/prod/: {len(links)}")

for a in links[:5]:
    href = a.get("href", "")
    # Find name inside - might be in a title attr, or inside an h2/h3
    name = a.get("title") or a.get_text(strip=True) or ""
    img = a.find("img")
    img_src = img.get("src") if img and img.has_attr("src") else (img.get("data-src") if img else "")
    print(f"\n  Nombre: {name[:60]}")
    print(f"  Link: {href}")
    print(f"  Img: {img_src}")

# Also check for price elements
for cls in ["price", "preco", "valor", "amount"]:
    els = soup.select(f".{cls}")
    if els:
        print(f"\nPrecios .{cls}: {len(els)} encontrados")
        for e in els[:3]:
            print(f"  {e.get_text(strip=True)[:30]}")
