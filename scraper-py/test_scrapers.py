import sys
sys.stdout.reconfigure(encoding='utf-8')

from common import fetch_html
from stores import cellshop, visaovip, nissei, megaelectronicos, shoppingchina, bristol, guaranielectro, tiendamovil, electronica, electropar, casarica, intershop

SCRAPERS = [
    ("cellshop", cellshop, "query"),
    ("nissei", nissei, "query"),
    ("megaelectronicos", megaelectronicos, "query"),
    ("shoppingchina", shoppingchina, "query"),
    ("bristol", bristol, "query"),
    ("guaranielectro", guaranielectro, "query"),
    ("tiendamovil", tiendamovil, "query"),
    ("electronica", electronica, "query"),
    ("electropar", electropar, "query"),
    ("casarica", casarica, "query"),
    ("intershop", intershop, "query"),
    ("visaovip", visaovip, "fixed"),
]

for name, mod, typ in SCRAPERS:
    try:
        if typ == "query":
            r = mod.scrape("celular")
        else:
            r = mod.scrape()
        print(f"[{'OK' if len(r) > 0 else 'NO'}] {name}: {len(r)} productos")
        if r:
            p = r[0]
            print(f"    -> {p['external_id']}: {p['name'][:60]}")
    except Exception as e:
        print(f"[ERR] {name}: {e}")
