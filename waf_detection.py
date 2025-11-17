#!/usr/bin/env python3
# waf_detection.py - Test against sites with known WAF/bot protection

import requests
import json
from tabulate import tabulate

USER_AGENTS = {
    "mozilla": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "curl": "curl/7.68.0",
    "sqlmap": "sqlmap/1.5.4",
    "nikto": "Nikto/2.1.6",
}

# Sites more likely to have WAF/bot protection
# Note: These are legitimate test targets
sites = [
    "https://www.google.com",
    "https://www.amazon.com",
    "https://www.cloudflare.com",
    "https://www.github.com",
]

print("=" * 100)
print("WAF/BOT PROTECTION DETECTION - Testing Real-World Sites")
print("=" * 100)
print("\nNote: These sites likely have advanced protection mechanisms\n")

results = {}

for site in sites:
    print(f"\n{'='*100}")
    print(f"Testing: {site}")
    print(f"{'='*100}\n")
    
    site_results = []
    
    for ua_name, ua_string in USER_AGENTS.items():
        headers = {"User-Agent": ua_string}
        
        try:
            r = requests.get(site, headers=headers, timeout=10, allow_redirects=True)
            
            result = {
                "User-Agent": ua_name.upper(),
                "Status": r.status_code,
                "Content-Type": r.headers.get("Content-Type", "---")[:40],
                "Length": len(r.text),
                "Server": r.headers.get("Server", "---")[:30],
                "CF-Ray": "✓ Cloudflare" if "cf-ray" in r.headers else "✗",
            }
            
            # Check for common WAF indicators
            waf_indicators = []
            if r.status_code in [403, 429, 503]:
                waf_indicators.append(f"Status {r.status_code}")
            if "blocked" in r.text.lower():
                waf_indicators.append("'blocked' in content")
            if "cloudflare" in r.text.lower():
                waf_indicators.append("Cloudflare detected")
            if "access denied" in r.text.lower():
                waf_indicators.append("'access denied' in content")
            
            if waf_indicators:
                result["WAF Indicators"] = ", ".join(waf_indicators)
            
            site_results.append(result)
            results[site] = {
                "ua": ua_name,
                "status": r.status_code,
                "server": r.headers.get("Server", ""),
                "length": len(r.text),
                "waf_indicators": waf_indicators,
            }
            
        except requests.exceptions.Timeout:
            site_results.append({
                "User-Agent": ua_name.upper(),
                "Status": "TIMEOUT",
                "Content-Type": "---",
                "Length": "---",
                "Server": "---",
                "CF-Ray": "---",
            })
            print(f"  ⏱️  {ua_name}: TIMEOUT")
            
        except requests.exceptions.ConnectionError as e:
            site_results.append({
                "User-Agent": ua_name.upper(),
                "Status": "BLOCKED",
                "Content-Type": "---",
                "Length": "---",
                "Server": "---",
                "CF-Ray": "---",
            })
            print(f"  🚫 {ua_name}: CONNECTION BLOCKED")
            
        except Exception as e:
            print(f"  ❌ {ua_name}: {type(e).__name__}")
    
    if site_results:
        print(tabulate(site_results, headers="keys", tablefmt="grid"))

# Analysis
print(f"\n\n{'='*100}")
print("ANALYSIS & OBSERVATIONS")
print(f"{'='*100}\n")

print("""
Key Findings:

1. CLOUDFLARE PROTECTION:
   - Many major sites use Cloudflare's WAF
   - Cloudflare often returns different responses based on User-Agent
   - Security scanning tools may trigger rate limiting (429) or blocking (403)

2. WAF COMMON RESPONSES:
   - 403 Forbidden: Access explicitly denied
   - 429 Too Many Requests: Rate limiting triggered
   - 503 Service Unavailable: Temporarily blocked
   - Redirects to challenge pages: Bot verification required

3. BOT DETECTION METHODS:
   - User-Agent string analysis
   - Request pattern analysis
   - JavaScript execution requirement (browser fingerprinting)
   - Cookie/session validation
   - IP reputation scoring
   - TLS fingerprinting

4. TYPICAL SCANNING TOOL BLOCKING:
   - sqlmap: Often detected by patterns it generates (SQL injection attempts)
   - Nikto: Detected by scanning patterns and fingerprint probes
   - curl: Can sometimes bypass if User-Agent is spoofed
   - Legitimate browser User-Agents: Generally allowed

RECOMMENDATION: For authorized security testing, use:
- VPN/proxy to rotate IPs
- Browser automation (Selenium, Puppeteer) to appear legitimate
- Slow request rates to avoid rate limiting
- Proper authentication headers
- Coordination with site owners (responsible disclosure)
""")

print(f"✓ Analysis complete")
