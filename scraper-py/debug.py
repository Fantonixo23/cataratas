import sys
sys.stdout.reconfigure(encoding='utf-8')
from common import fetch_html

# Test nissei
url = "https://nissei.com/py/iphone"
print("Nissei URL:", url)
soup = fetch_html(url)
print("Nissei title:", soup.title.string if soup.title else "NO TITLE")
cards = soup.select("article, .product-item, [class*=product]")
print(f"Nissei cards found: {len(cards)}")
if cards:
    print("First card HTML:", str(cards[0])[:300])
