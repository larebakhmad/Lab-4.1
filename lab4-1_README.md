# Lab 4.1: HTTP Header Analysis & Web Reconnaissance

## Overview
Passive web reconnaissance analyzing HTTP headers, page metadata, and content patterns. Explores defensive applications and ethical considerations for security testing.

---

## Server Headers Observed & Usefulness

**Findings**:
- **scanme.nmap.org**: Apache/2.4.7 (Ubuntu) — full version exposed
- **example.com**: Hidden server (best practice)
- **httpbin.org**: gunicorn/19.9.0 (Python framework visible)
- **WAF-protected sites**: Cloudflare, Amazon (selective blocking)

**Usefulness**: Moderately helpful for reconnaissance:
- Reveals technology stack (Apache, IIS, nginx)
- Indicates OS hints and framework types
- Shows CDN usage (Akamai, Cloudflare)
- Server hiding is a security indicator

Headers alone don't reveal vulnerabilities—they're baseline reconnaissance data.

---

## Key Differences Between Target Sites

| Site | Server | WAF | Detection |
|------|--------|-----|-----------|
| **scanme.nmap.org** | Apache/2.4.7 | None | All User-Agents allowed |
| **example.com** | Hidden | None | Minimal content; no forms |
| **httpbin.org** | gunicorn | None | API testing service |
| **Cloudflare** | Cloudflare | Yes | -35 to -45 byte content changes |
| **Amazon** | Amazon | Yes | Challenge pages (+700KB) on suspicious referers |

**Cloudflare** detects spoofed X-Forwarded-For and sqlmap signatures via subtle response modifications. **Amazon** serves JavaScript challenges for suspicious headers while trusting legitimate proxy headers.

---

## One Defensive Application

**Implement Header Anomaly Detection in WAF Rules**:

```python
suspicious_score = 0
if X-Forwarded-For == spoofed_private_IP:
    suspicious_score += 2
if Referer == malicious_domain:
    suspicious_score += 3
if X-Scanner header present:
    suspicious_score += 5
if multiple_suspicious_headers:
    suspicious_score += 4
    
if suspicious_score >= 5:
    return CHALLENGE_PAGE  # JS verification
elif suspicious_score >= 8:
    return 403_FORBIDDEN   # Block
```

This graduated response maximizes security while minimizing false positives from legitimate proxies.

---

## Ethical Precautions for Security Testing

1. **Authorization**: Get explicit written permission before testing any system
2. **Scope Definition**: Document approved domains, endpoints, timeframes
3. **Minimize Impact**: Space requests appropriately; respect robots.txt
4. **Data Privacy**: Don't capture PII; report exposures immediately
5. **Responsible Disclosure**: Report via security@domain.com; allow 90 days for patches
6. **Legal Compliance**: Verify local laws; unauthorized testing may violate CFAA, GDPR, CCPA
7. **Maintain Audit Trails**: Document all requests and findings

---

## Deliverables

**Core Scripts**:
- ✅ `lab4-1_get.py` — Header extraction
- ✅ `lab4-1_collect_headers.py` — Batch collection
- ✅ `lab4-1_parse.py` — HTML parsing
- ✅ `lab4-1_header_probe.py` — Multi-User-Agent testing

**Data Outputs**:
- ✅ `Headers.json` — Server headers from target sites
- ✅ `header_probe_comparison.json` — User-Agent probe results
- ✅ `advanced_header_fuzzing.json` — WAF detection results
- ✅ `keyword_results_detailed.json` — Keyword analysis

**Bonus Extensions**:
- ✅ `lab4-1_report_generator.py` — Auto-generates markdown summary
- ✅ `advanced_header_fuzzing.py` — WAF detection mechanism analysis
- ✅ `user_agent_analysis.py` — Scanner tool detection patterns
- ✅ Framework fingerprinting via headers/paths

---

**Word Count**: 359 words | **Status**: ✅ Complete
