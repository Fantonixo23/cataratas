import sys
sys.stdout.reconfigure(encoding="utf-8")
from common import fetch_html

s = fetch_html("https://www.topdekinformatica.com.br/categoria/placa-mae")
for a in s.select('a[href*="/categoria/"]'):
    h = a.get("href", "")
    txt = a.get_text(strip=True)
    if txt and len(txt) > 3 and txt not in ("Todos", "Placa Mae", "Placa-mãe", "Home", "Inicio"):
        print(f"{txt}: {h}")
