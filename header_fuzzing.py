#!/usr/bin/env python3
# header_fuzzing.py - Fuzz different header combinations and log response changes

import requests
import json
from tabulate import tabulate
from collections import defaultdict

# Test sites
sites = [
    "http://example.com",
    "http://info.cern.ch",
    "http://scanme.nmap.org",
]

# Header combinations to test
header_variations = {
    "baseline": {},
    
    "x_forwarded_for": {
        "X-Forwarded-For": "1.2.3.4",
    },
    
    "referer_evil": {
        "Referer": "http://evil.example/",
    },
    
    "accept_language": {
        "Accept-Language": "fr-FR",
    },
    
    "suspicious_combo": {
        "X-Forwarded-For": "1.2.3.4",
        "Referer": "http://evil.example/",
        "Accept-Language": "fr-FR",
        "X-Requested-With": "XMLHttpRequest",
    },
    
    "proxy_headers": {
        "X-Forwarded-For": "192.168.1.1",
        "X-Real-IP": "10.0.0.1",
        "X-Forwarded-Proto": "https",
    },
    
    "scanner_headers": {
        "X-Scanner": "nmap",
        "X-Scan-Memo": "port scan",
    },
    
    "mobile_spoofing": {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)",
        "Accept-Language": "en-US",
    },
}

print("=" * 120)
print("HEADER FUZZING - Testing Response Changes")
print("=" * 120)

all_results = {}

for site in sites:
    print(f"\n{'='*120}")
    print(f"Target: {site}")
    print(f"{'='*120}\n")
    
    baseline_response = None
    site_results = []
    
    for variation_name, headers in header_variations.items():
        try:
            r = requests.get(site, headers=headers, timeout=5)
            
            response_data = {
                "variation": variation_name,
                "status": r.status_code,
                "content_length": len(r.text),
                "headers": dict(r.headers),
                "body_hash": hash(r.text) % (10**8),  # Simple hash for comparison
            }
            
            # Store baseline
            if variation_name == "baseline":
                baseline_response = response_data
                site_results.append({
                    "Headers": variation_name,
                    "Status": r.status_code,
                    "Length": len(r.text),
                    "Changed": "BASELINE",
                    "Interesting": "---",
                })
            else:
                # Compare to baseline
                status_changed = baseline_response["status"] != r.status_code
                length_changed = baseline_response["content_length"] != len(r.text)
                
                change_indicator = ""
                if status_changed or length_changed:
                    change_indicator = "🔴 CHANGED"
                    
                interesting_notes = []
                if status_changed:
                    interesting_notes.append(f"Status: {baseline_response['status']}→{r.status_code}")
                if length_changed:
                    interesting_notes.append(f"Length: {baseline_response['content_length']}→{len(r.text)}")
                
                site_results.append({
                    "Headers": variation_name,
                    "Status": r.status_code,
                    "Length": len(r.text),
                    "Changed": change_indicator,
                    "Interesting": "; ".join(interesting_notes) if interesting_notes else "---",
                })
            
            all_results.setdefault(site, {})[variation_name] = response_data
            
        except requests.exceptions.RequestException as e:
            site_results.append({
                "Headers": variation_name,
                "Status": "ERROR",
                "Length": "---",
                "Changed": "ERROR",
                "Interesting": str(e)[:40],
            })
    
    print(tabulate(site_results, headers="keys", tablefmt="grid"))

# Detailed analysis
print(f"\n\n{'='*120}")
print("DETAILED ANALYSIS - ANOMALIES & CHANGES")
print(f"{'='*120}\n")

for site, variations in all_results.items():
    print(f"\n📍 {site}")
    print("-" * 120)
    
    if "baseline" not in variations:
        print("  (No baseline found)")
        continue
    
    baseline = variations["baseline"]
    changes_found = False
    
    for var_name, var_data in variations.items():
        if var_name == "baseline":
            continue
        
        if "error" in var_data:
            print(f"  ❌ {var_name}: ERROR - {var_data['error']}")
            changes_found = True
            continue
        
        status_diff = var_data["status"] != baseline["status"]
        length_diff = var_data["content_length"] != baseline["content_length"]
        
        if status_diff or length_diff:
            print(f"\n  🔴 {var_name.upper()}")
            if status_diff:
                print(f"     Status: {baseline['status']} → {var_data['status']}")
            if length_diff:
                print(f"     Length: {baseline['content_length']} → {var_data['content_length']} bytes")
            
            # Show headers that were sent
            print(f"     Headers sent: {var_name.split('_')[0]}")
            changes_found = True
    
    if not changes_found:
        print("  ✓ No changes detected with any header variations")

# Summary statistics
print(f"\n\n{'='*120}")
print("SUMMARY STATISTICS")
print(f"{'='*120}\n")

total_variations = len(header_variations) - 1  # exclude baseline
sites_tested = len(all_results)
total_tests = total_variations * sites_tested

print(f"Total tests performed: {total_tests}")
print(f"Sites tested: {sites_tested}")
print(f"Header variations: {total_variations}\n")

# Count changes
changes_by_site = defaultdict(list)
for site, variations in all_results.items():
    if "baseline" not in variations:
        continue
    baseline = variations["baseline"]
    for var_name, var_data in variations.items():
        if var_name != "baseline" and "error" not in var_data:
            if var_data["status"] != baseline["status"] or var_data["content_length"] != baseline["content_length"]:
                changes_by_site[site].append(var_name)

print("Response changes detected:")
if changes_by_site:
    for site, changes in changes_by_site.items():
        print(f"  {site}: {len(changes)} variation(s) triggered changes")
        for change in changes:
            print(f"    - {change}")
else:
    print("  ✓ No response changes detected on any tested sites")

# Save detailed results
output_file = "/workspaces/Lab-4.1/header_fuzzing_results.json"
with open(output_file, "w") as f:
    # Convert unhashable types for JSON serialization
    for site in all_results:
        for var in all_results[site]:
            if "headers" in all_results[site][var]:
                all_results[site][var]["headers"] = {k: str(v) for k, v in all_results[site][var]["headers"].items()}
    json.dump(all_results, f, indent=2)

print(f"\n✓ Detailed results saved to: {output_file}")
