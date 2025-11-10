#!/usr/bin/env python3
# lab4-1_parse.py
from bs4 import BeautifulSoup
import requests, json, sys, urllib.parse

def parse_page(url, out_file=None):
    r = requests.get(url, timeout=5)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else None
    meta = soup.find("meta", attrs={"name": "description"})
    meta_desc = meta["content"].strip() if meta and meta.get("content") else None

    forms = []
    for f in soup.find_all("form"):
        method = f.get("method", "GET").upper()
        action = urllib.parse.urljoin(url, f.get("action", ""))
        inputs = []
        for inp in f.find_all("input"):
            inputs.append({
                "name": inp.get("name"),
                "type": inp.get("type"),
                "value": inp.get("value")
            })
        forms.append({"method": method, "action": action, "inputs": inputs})

    result = {
        "url": url,
        "title": title,
        "meta_description": meta_desc,
        "forms": forms
    }

    if out_file:
        with open(out_file, "w") as fh:
            json.dump(result, fh, indent=2)
    print(json.dumps(result, indent=2))
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python lab1_parse.py <url> [out_file.json]")
        sys.exit(1)
    parse_page(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)