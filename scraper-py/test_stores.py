from curl_cffi import requests

stores = {
    "Atacado Games": "https://www.atacadogames.com.py/buscar?q=iphone",
    "Cellshop": "https://www.cellshop.com.py/catalogsearch/result/?q=iphone",
    "Visaovip": "https://www.visaovip.com/catalogsearch/result/?q=iphone",
}

for name, url in stores.items():
    try:
        resp = requests.get(url, headers={"Accept-Language": "es-PY,es;q=0.9"}, impersonate="chrome124", timeout=10)
        print(f"\n=== {name} ===")
        print(f"Status: {resp.status_code}")
        print(f"Title: {resp.text[resp.text.find('<title>')+7:resp.text.find('</title>')][:100] if '<title>' in resp.text else 'N/A'}")
        print(f"Length: {len(resp.text)} chars")
        if resp.status_code == 200:
            for cls in ["product-item", "product", "item", "card"]:
                count = resp.text.count(f'class="{cls}')
                if count:
                    print(f"  .{cls}: {count} matches")
    except Exception as e:
        print(f"\n=== {name} ===")
        print(f"ERROR: {e}")
