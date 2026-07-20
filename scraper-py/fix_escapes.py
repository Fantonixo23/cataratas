import os, re

stores_dir = os.path.join(os.path.dirname(__file__), "stores")

for fname in os.listdir(stores_dir):
    if not fname.endswith(".py"):
        continue
    path = os.path.join(stores_dir, fname)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Fix double-escaped backslashes
    content = content.replace("\\\\\\\\d", "\\\\d")
    # Fix raw string issues
    content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Fixed: {fname}")
