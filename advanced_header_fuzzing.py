#!/usr/bin/env python3
# advanced_header_fuzzing.py - Enhanced fuzzing with header inspection and WAF targets

import requests
import json
from tabulate import tabulate
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# Test sites with known WAF protection
sites = [
    "https://www.cloudflare.com",
    "https://www.amazon.com",
]

# Header combinations to test
header_variations = {
    "baseline": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    },
    
    "x_forwarded_for": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-Forwarded-For": "1.2.3.4",
    },
    
    "suspicious_referer": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "http://evil.example/",
    },
    
    "sqlmap_signature": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-Forwarded-For": "1.2.3.4",
        "Referer": "http://evil.example/",
        "Accept-Language": "fr-FR",
    },
    
    "proxy_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-Forwarded-For": "192.168.1.1",
        "X-Real-IP": "10.0.0.1",
        "X-Forwarded-Proto": "https",
        "X-Forwarded-Host": "internal.example.com",
    },
    
    "scanner_markers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-Scanner": "nmap",
        "X-Scan-Memo": "port scan",
        "X-Originating-IP": "[192.168.0.1]",
    },
}

print("=" * 140)
print("ADVANCED HEADER FUZZING - Testing WAF Response Variations")
print("=" * 140)

all_results = {}

for site in sites:
    print(f"\n{'='*140}")
    print(f"Target: {site}")
    print(f"{'='*140}\n")
    
    baseline_response = None
    site_results = []
    site_details = {}
    
    for variation_name, headers in header_variations.items():
        try:
            # Create session with retries
            session = requests.Session()
            retry = Retry(connect=1, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            
            r = session.get(site, headers=headers, timeout=10, verify=False, allow_redirects=True)
            
            # Extract interesting response headers
            waf_headers = {
                "CF-Ray": r.headers.get("CF-Ray", "---"),
                "CF-Cache-Status": r.headers.get("CF-Cache-Status", "---"),
                "Server": r.headers.get("Server", "---"),
                "X-Frame-Options": r.headers.get("X-Frame-Options", "---"),
                "X-Content-Type-Options": r.headers.get("X-Content-Type-Options", "---"),
                "Strict-Transport-Security": r.headers.get("Strict-Transport-Security", "---")[:30],
            }
            
            response_data = {
                "variation": variation_name,
                "status": r.status_code,
                "content_length": len(r.text),
                "headers_sent": headers,
                "response_headers": waf_headers,
                "has_challenge": "challenge" in r.text.lower() or "verify" in r.text.lower(),
                "has_blocked": "blocked" in r.text.lower() or "access denied" in r.text.lower(),
            }
            
            site_details[variation_name] = response_data
            
            # Store baseline
            if variation_name == "baseline":
                baseline_response = response_data
                site_results.append({
                    "Headers": variation_name,
                    "Status": r.status_code,
                    "Length": len(r.text),
                    "CF-Ray": waf_headers.get("CF-Ray", "---")[:20],
                    "Changed": "BASELINE",
                    "Alerts": "---",
                })
            else:
                # Compare to baseline
                status_changed = baseline_response["status"] != r.status_code
                length_changed = baseline_response["content_length"] != len(r.text)
                
                alerts = []
                if status_changed:
                    alerts.append(f"Status {baseline_response['status']}→{r.status_code}")
                if length_changed:
                    diff = len(r.text) - baseline_response["content_length"]
                    alerts.append(f"Length {diff:+d}b")
                if response_data["has_challenge"] and not baseline_response.get("has_challenge"):
                    alerts.append("Challenge page detected")
                if response_data["has_blocked"] and not baseline_response.get("has_blocked"):
                    alerts.append("Blocked/Denied detected")
                
                change_indicator = "🔴" if alerts else ""
                
                site_results.append({
                    "Headers": variation_name,
                    "Status": r.status_code,
                    "Length": len(r.text),
                    "CF-Ray": waf_headers.get("CF-Ray", "---")[:20],
                    "Changed": change_indicator,
                    "Alerts": "; ".join(alerts) if alerts else "---",
                })
            
            all_results[site] = site_details
            
        except requests.exceptions.Timeout:
            site_results.append({
                "Headers": variation_name,
                "Status": "TIMEOUT",
                "Length": "---",
                "CF-Ray": "---",
                "Changed": "⚠️",
                "Alerts": "Request timeout",
            })
        except requests.exceptions.ConnectionError as e:
            site_results.append({
                "Headers": variation_name,
                "Status": "ERROR",
                "Length": "---",
                "CF-Ray": "---",
                "Changed": "🔴",
                "Alerts": "Connection blocked",
            })
        except Exception as e:
            site_results.append({
                "Headers": variation_name,
                "Status": "ERROR",
                "Length": "---",
                "CF-Ray": "---",
                "Changed": "❌",
                "Alerts": str(e)[:30],
            })
    
    print(tabulate(site_results, headers="keys", tablefmt="grid"))

# Detailed anomaly analysis
print(f"\n\n{'='*140}")
print("DETAILED ANOMALY ANALYSIS")
print(f"{'='*140}\n")

for site, variations in all_results.items():
    print(f"\n📍 {site}")
    print("-" * 140)
    
    if "baseline" not in variations:
        print("  (No baseline found)")
        continue
    
    baseline = variations["baseline"]
    anomalies_found = False
    
    for var_name, var_data in variations.items():
        if var_name == "baseline":
            continue
        
        status_diff = var_data["status"] != baseline["status"]
        length_diff = var_data["content_length"] != baseline["content_length"]
        challenge_new = var_data.get("has_challenge") and not baseline.get("has_challenge")
        blocked_new = var_data.get("has_blocked") and not baseline.get("has_blocked")
        
        if status_diff or length_diff or challenge_new or blocked_new:
            print(f"\n  🔴 {var_name.upper()}")
            print(f"     Headers: {dict(var_data['headers_sent'])}")
            if status_diff:
                print(f"     🔔 Status: {baseline['status']} → {var_data['status']}")
            if length_diff:
                diff = var_data['content_length'] - baseline['content_length']
                print(f"     🔔 Length: {baseline['content_length']} → {var_data['content_length']} ({diff:+d} bytes)")
            if challenge_new:
                print(f"     🔔 Challenge/Verification page detected")
            if blocked_new:
                print(f"     🔔 Access blocked/denied message found")
            anomalies_found = True
    
    if not anomalies_found:
        print("  ✓ No anomalies detected with header variations")

# Summary
print(f"\n\n{'='*140}")
print("SUMMARY")
print(f"{'='*140}\n")

print("Key Findings:\n")
print("1. X-Forwarded-For header:")
print("   → Used to spoof the client's real IP address")
print("   → May be logged or filtered by WAF if not trusted")
print()
print("2. Referer header:")
print("   → Setting suspicious referer may trigger WAF rules")
print("   → Often used in CSRF attack detection")
print()
print("3. Accept-Language:")
print("   → Usually safe, but combinations may be flagged")
print()
print("4. Proxy/Internal headers:")
print("   → X-Forwarded-* and X-Real-IP headers indicate proxied requests")
print("   → May reveal or bypass WAF if misconfigured")
print()
print("5. Scanner headers:")
print("   → Custom headers with 'scan' or 'nmap' are typically blocked immediately")
print()

# Save results
output_file = "/workspaces/Lab-4.1/advanced_header_fuzzing.json"
with open(output_file, "w") as f:
    json.dump(all_results, f, indent=2, default=str)

print(f"\n✓ Detailed results saved to: {output_file}")
