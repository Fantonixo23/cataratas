import sys
sys.stdout.reconfigure(encoding="utf-8")
from common import fetch_html

# Try atacadoconnect with search results
s = fetch_html("https://www.atacadoconnect.com/busca?q=iphone")
print(f"Title: {s.title.string if s.title else 'NONE'}")

# Look for product cards in search results
for sel in [".product-item", ".card", ".item", "[class*=product]", ".vitrine-produto",
            ".box-produto", ".product", ".shelf-item", ".listagem-item", "li[class]",
            ".produto-item", ".search-result-item", "a[href*='produto']"]:
    cards = s.select(sel)
    if cards:
        sample = cards[0].get_text(strip=True)[:60] if len(cards) > 0 else ""
        print(f"  {sel}: {len(cards)} [{sample}]")
        if len(cards) > 3:
            # Print first card's HTML
            print(f"    HTML: {str(cards[0])[:400]}")
            break
