import os
import sys
import time
import json
import subprocess

from dotenv import load_dotenv
from supabase import create_client

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

from run_all_stores import STORE_MODULES, run_store, upsert, load_existing_ids

TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 24000
HERE = os.path.dirname(os.path.abspath(__file__))
SHOP_CKPT = os.path.join(HERE, "checkpoint_shoppingchina.json")
SHOP_TOTAL = 29773


def total_count():
    r = sb.table("products").select("id", count="exact").execute()
    return r.count or 0


def shop_done_count():
    try:
        with open(SHOP_CKPT, "r", encoding="utf-8") as f:
            ck = json.load(f)
        return len(ck.get("done", {}))
    except Exception:
        return 0


class ShoppingRunner:
    def __init__(self):
        self.proc = None

    def spawn(self):
        log = open(os.path.join(HERE, "shop.log"), "a", encoding="utf-8")
        self.proc = subprocess.Popen(
            [sys.executable, "run_catalog.py"],
            cwd=HERE,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        print(f"  [shoppingchina] iniciado PID={self.proc.pid}", flush=True)

    def ensure(self):
        if self.proc is not None and self.proc.poll() is None:
            return
        if shop_done_count() >= SHOP_TOTAL and total_count() >= TARGET:
            return
        print("  [shoppingchina] proceso muerto, relanzando (checkpoint resumible)", flush=True)
        self.spawn()


def sweep_store(name):
    try:
        uniq = run_store(name)
        existing = load_existing_ids(name)
        new = [p for p in uniq if str(p.get("external_id")) not in existing]
        if new:
            upsert(new)
            print(f"  [{name}] subidos {len(new)} de {len(uniq)}", flush=True)
        else:
            print(f"  [{name}] nada nuevo (ya en DB)", flush=True)
    except Exception as e:
        print(f"  [{name}] error: {type(e).__name__}: {e}", flush=True)


def main():
    sh = ShoppingRunner()
    last = 0
    while True:
        c = total_count()
        if c >= TARGET:
            print(f"DONE: {c} productos, objetivo {TARGET} alcanzado", flush=True)
            break
        if c != last:
            print(f"TOTAL ACTUAL: {c} / {TARGET}", flush=True)
            last = c

        sh.ensure()

        # ciclo completo por todas las tiendas (no-supermercado)
        for name in STORE_MODULES:
            sweep_store(name)

        # pequeña pausa antes de re-medir
        time.sleep(2)


if __name__ == "__main__":
    main()