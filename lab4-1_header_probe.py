#!/usr/bin/env python3
# lab4-1_header_probe.py
import requests, sys, csv

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "curl/7.68.0",
    "sqlmap/1.5.4",
    "Nikto/2.1.6",
    "python-requests/2.x"
]

def probe(url, out_csv=None):
    rows = []
    for ua in USER_AGENTS:
        headers = {"User-Agent": ua}
        try:
            r = requests.get(url, headers=headers, timeout=5)
            rows.append({
                "ua": ua,
                "status": r.status_code,
                "server": r.headers.get("Server", ""),
                "length": len(r.text)
            })
        except requests.exceptions.RequestException as e:
            rows.append({"ua": ua, "error": str(e)})
    if out_csv:
        with open(out_csv, "w", newline='') as fh:
            writer = csv.DictWriter(fh, fieldnames=["ua","status","server","length","error"])
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
    for r in rows:
        print(r)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python lab1_header_probe.py <url> [out.csv]")
        sys.exit(1)
    probe(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)