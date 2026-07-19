import sys
sys.stdout.reconfigure(encoding='utf-8')

from common import fetch_html

soup = fetch_html("https://visaovip.com/es/")
links = soup.select("a[href*='/es/prod/']")

# Look at one product card's full HTML
card = links[0].find_parent()
while card and card.name != "div":
    card = card.find_parent()

# Print the relevant HTML structure
for cls in ["col-6", "md:col-4", "product"]:
    cards = soup.select(f".{cls}")
    if cards:
        print(f"Cards con .{cls}: {len(cards)}")
        # Print structure of first one
        first = cards[0]
        print(f"  HTML structure:")
        for child in first.descendants:
            if child.name and child.name in ["a", "img", "span", "div", "p", "h2", "h3"]:
                txt = child.get_text(strip=True)[:40] if child.get_text(strip=True) else ""
                src = child.get("src", "")[:50] if child.name == "img" else ""
                cls_str = " ".join(child.get("class", [])) if child.has_attr("class") else ""
                if txt or src:
                    print(f"    <{child.name} class='{cls_str[:30]}'> {txt or src}")
        break

# Find any element with $ or U$ or price
for el in soup.find_all(string=re.compile(r"U\$|price|pre[cç]o", re.I)):
    parent = el.parent
    if parent:
        cls = " ".join(parent.get("class", [])) if parent.has_attr("class") else ""
        tag = parent.name
        print(f"\nPrice element: <{tag} class='{cls[:40]}'> {el[:60]}")
