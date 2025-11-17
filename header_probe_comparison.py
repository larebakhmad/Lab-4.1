#!/usr/bin/env python3
# header_probe_comparison.py - Compare header probe results across multiple sites

import requests
import csv
import json
from collections import defaultdict
from tabulate import tabulate

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "curl/7.68.0",
    "sqlmap/1.5.4",
    "Nikto/2.1.6",
    "python-requests/2.x"
]

sites = [
    "http://example.com",
    "http://info.cern.ch",
    "http://scanme.nmap.org",
    "http://httpbin.org/status/200",
]

all_results = {}

print("=" * 80)
print("HEADER PROBE COMPARISON - TESTING MULTIPLE USER AGENTS ACROSS SITES")
print("=" * 80)

for site in sites:
    print(f"\n{'='*80}")
    print(f"Probing: {site}")
    print(f"{'='*80}")
    
    rows = []
    for ua in USER_AGENTS:
        headers = {"User-Agent": ua}
        try:
            r = requests.get(site, headers=headers, timeout=5)
            row = {
                "User-Agent": ua.split('/')[0],  # Shorten for display
                "Status": r.status_code,
                "Server": r.headers.get("Server", "---"),
                "Length": len(r.text),
                "Content-Type": r.headers.get("Content-Type", "---"),
            }
            rows.append(row)
            all_results.setdefault(site, []).append({
                "ua": ua,
                "status": r.status_code,
                "server": r.headers.get("Server", ""),
                "length": len(r.text),
                "content_type": r.headers.get("Content-Type", ""),
            })
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error with {ua}: {e}")
            all_results.setdefault(site, []).append({
                "ua": ua,
                "error": str(e),
            })
    
    if rows:
        print(tabulate(rows, headers="keys", tablefmt="grid"))

# Comparison summary
print(f"\n{'='*80}")
print("SUMMARY: STATUS, SERVER, AND LENGTH COMPARISON")
print(f"{'='*80}\n")

for site in sites:
    if site in all_results and all_results[site]:
        first_result = all_results[site][0]
        if "error" not in first_result:
            print(f"Site: {site}")
            print(f"  Status:  {first_result['status']}")
            print(f"  Server:  {first_result['server'] if first_result['server'] else '(None/Hidden)'}")
            print(f"  Length:  {first_result['length']} bytes")
            print()

# Detailed analysis
print(f"{'='*80}")
print("DETAILED ANALYSIS")
print(f"{'='*80}\n")

for site in sites:
    if site not in all_results:
        continue
    
    results = all_results[site]
    statuses = [r.get('status') for r in results if 'status' in r]
    lengths = [r.get('length') for r in results if 'length' in r]
    servers = [r.get('server') for r in results if 'server' in r and r['server']]
    
    print(f"📍 {site}")
    
    if statuses:
        # Check if status varies
        if len(set(statuses)) == 1:
            print(f"   ✓ Status consistent: {statuses[0]}")
        else:
            print(f"   ⚠️  Status varies: {set(statuses)}")
    
    if lengths:
        # Check if length varies
        if len(set(lengths)) == 1:
            print(f"   ✓ Content length consistent: {lengths[0]} bytes")
        else:
            print(f"   ⚠️  Content length varies: {set(lengths)}")
    
    if servers:
        # Check if server header varies
        if len(set(servers)) == 1:
            print(f"   ✓ Server header consistent: {servers[0]}")
        else:
            print(f"   ⚠️  Server header varies: {set(servers)}")
    elif not servers and results and 'server' in results[0]:
        print(f"   ℹ️  Server header: Not provided by server")
    
    print()

# Save detailed results
output_json = "/workspaces/Lab-4.1/header_probe_comparison.json"
with open(output_json, "w") as f:
    json.dump(all_results, f, indent=2)

print(f"✓ Results saved to: {output_json}")
