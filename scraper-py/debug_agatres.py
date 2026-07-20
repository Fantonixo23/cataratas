import sys
sys.stdout.reconfigure(encoding="utf-8")
from stores import agatres
print("Starting agatres scrape...")
r = agatres.scrape("")
print(f"Done. Result: {len(r)} products")
if r:
    print(f"First: {r[0]['name'][:40]}")
