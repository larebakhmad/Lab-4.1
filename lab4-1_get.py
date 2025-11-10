#!/usr/bin/env python3
# lab4-1_get.py
import requests
import sys

def simple_get(url):
    try:
        r = requests.get(url, timeout=5, allow_redirects=True)
        print(f"[+] URL: {url}")
        print(f"    Status Code: {r.status_code}")
        print(f"    Final URL:   {r.url}")
        print(f"    Content-Type: {r.headers.get('Content-Type', 'N/A')}")
        print(f"    Server:       {r.headers.get('Server', 'N/A')}")
        print(f"    Content-Length: {r.headers.get('Content-Length', 'Unknown')}")
        return r
    except requests.exceptions.RequestException as e:
        print(f"[!] Request error for {url}: {e}")
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python lab4-1_get.py <url>")
        sys.exit(1)
    simple_get(sys.argv[1])