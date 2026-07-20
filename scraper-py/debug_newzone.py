import urllib.request, re
from bs4 import BeautifulSoup

url = "https://newzone.com.py/"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
soup = BeautifulSoup(html, "html.parser")

# Find all product containers
for card in soup.select("[class*=product]"):
    imgs = card.select("img")
    links = card.select("a[href*='/producto/']")
    if imgs and links:
        href = links[0].get("href")
        img_src = imgs[0].get("src") or imgs[0].get("data-src") or ""
        print(f"IMG: {img_src[:100] if img_src else 'NONE'}")
        print(f"  href: {href}")
        print(f"  card class: {card.get('class')}")
        break
else:
    print("No product card found with both img and link")

# Try another approach - look at all images
print("\n--- All images near product links ---")
for a in soup.select("a[href*='/producto/']")[:3]:
    # Check inside the same parent container
    parent = a.parent
    img = parent.select_one("img")
    if not img:
        img = a.find_next("img")
    if not img:
        img = a.find_previous("img")
    if img:
        src = img.get("src") or img.get("data-src") or ""
        print(f"Found img: {src[:100]}")
    else:
        print(f"No img near: {a.get('href')}")
        # Print parent HTML
        print(f"  parent tag: {parent.name}, parent class: {parent.get('class')}")
        print(f"  parent HTML[:300]: {str(parent)[:300]}")
