from curl_cffi import requests

resp = requests.get(
    "https://www.nissei.com/py/catalogsearch/result/?q=iphone",
    headers={"Accept-Language": "es-PY,es;q=0.9"},
    impersonate="chrome124",
)
print("Status:", resp.status_code)
print("Headers:", dict(resp.headers))
print("Content (first 1000 chars):")
print(resp.text[:1000])
