import sys
sys.stdout.reconfigure(encoding="utf-8")
from common import fetch_html

s = fetch_html("https://www.lifebeach.com.py/")
for a in s.select('a[href*="/categoria/"]'):
    h = a.get("href", "")
    t = a.get_text(strip=True)
    if t and len(t) > 2:
        print(f"  {t}: {h}")
