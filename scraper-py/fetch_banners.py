import urllib.request, re, json, os

urls = {
    'shoppingchina': 'https://www.shoppingchina.com.py',
    'cellshop': 'https://www.cellshop.com.py',
    'visaovip': 'https://visaovip.com/es/',
    'newzone': 'https://www.newzone.com.py',
    'oneclick': 'https://www.oneclick.com.py',
}

all_banners = []

for name, url in urls.items():
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')

        # Find all image URLs in the HTML that look like banners
        # Look for images with banner/promo/slide keywords in the path or in nearby HTML
        found = []

        # Pattern 1: <img src="..."> with alt/title/class containing banner keywords
        for m in re.finditer(r'<img[^>]+src="([^"]+)"[^>]*>', html, re.I):
            tag = m.group(0)
            src = m.group(1)
            combined = tag.lower()
            keywords = ['banner', 'slide', 'slider', 'promo', 'popup', 'hotsite', 'homepage-beneficios', 'beneficios']
            if any(k in combined for k in keywords):
                if src.endswith(('.jpg', '.jpeg', '.png', '.webp')) and not src.startswith('data:'):
                    found.append(src)

        # Pattern 2: Inline styles with background-image
        for m in re.finditer(r'background(?:-image)?\s*:\s*url\(["\']?([^"\')]+)["\']?\)', html, re.I):
            src = m.group(1)
            tag_context = html[max(0, m.start()-200):m.end()+200].lower()
            keywords = ['banner', 'slide', 'slider', 'promo', 'hero', 'carousel']
            if any(k in tag_context for k in keywords):
                if src.endswith(('.jpg', '.jpeg', '.png', '.webp')) and not src.startswith('data:'):
                    found.append(src)

        # Pattern 3: Look for images inside sections with slider/carousel classes
        for m in re.finditer(r'<section[^>]*(?:carousel|slider|banner)[^>]*>.*?<img[^>]+src="([^"]+)"', html, re.I | re.DOTALL):
            src = m.group(1)
            if src.endswith(('.jpg', '.jpeg', '.png', '.webp')) and not src.startswith('data:'):
                found.append(src)

        # Resolve relative URLs
        resolved = []
        for src in found:
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = url.rstrip('/') + src
            elif not src.startswith('http'):
                src = url.rstrip('/') + '/' + src
            resolved.append(src)

        # Deduplicate
        seen = set()
        unique = []
        for src in resolved:
            if src not in seen:
                seen.add(src)
                unique.append(src)

        all_banners.append({
            'store': name,
            'url': url,
            'banners': unique[:30],
        })
        print(f'{name}: {len(unique)} banners')
        for b in unique[:5]:
            print(f'  {b[:120]}')
    except Exception as e:
        print(f'{name}: ERROR - {e}')
        all_banners.append({'store': name, 'url': url, 'banners': [], 'error': str(e)})

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'banners.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(all_banners, f, ensure_ascii=False, indent=2)
print(f'Saved to {out}')
