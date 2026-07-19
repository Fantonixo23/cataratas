import sys, re
sys.stdout.reconfigure(encoding='utf-8')

from common import fetch_html

soup = fetch_html("https://visaovip.com/es/")

# Method 1: direct attr selector
links1 = soup.select("a[href*='/es/prod/']")
print(f"Metodo 1 (a[href*='/es/prod/']): {len(links1)}")

# Method 2: find all a tags and filter
all_a = soup.find_all("a")
links2 = [a for a in all_a if a.get("href") and "/es/prod/" in a["href"]]
print(f"Metodo 2 (find_all + filter): {len(links2)}")

# Method 3: check if any links at all
print(f"\nTotal <a> tags: {len(all_a)}")
for a in all_a[:20]:
    href = a.get("href", "")
    if "/es/prod/" in href:
        print(f"  FOUND: {href[:70]}")
    elif href and not href.startswith("#") and not href.startswith("javascript"):
        pass  # Other links

# Check for iframes or JS placeholders
iframes = soup.find_all("iframe")
print(f"\nIframes: {len(iframes)}")
scripts = soup.find_all("script", src=True)
print(f"Scripts externos: {len(scripts)}")

# Check if products are loaded via JSON in script tags
for script in soup.find_all("script"):
    if script.string and ("prod" in script.string or "product" in script.string.lower()):
        print(f"\nScript con 'prod': {script.string[:100]}...")
