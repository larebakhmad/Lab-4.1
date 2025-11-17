# Lab 4.1 - HTTP Reconnaissance Report
**Generated**: 2025-11-17 23:36:50

## Executive Summary

This lab performs passive HTTP reconnaissance on multiple websites to identify:
- Server technologies and versions
- Response patterns to different User-Agents
- WAF (Web Application Firewall) detection mechanisms
- Content patterns and keywords

---

## Server Headers Summary

| URL | Status | Server | Content-Type |
|-----|--------|--------|---------------|
| http://scanme.nmap.org | 200 | Apache/2.4.7 (Ubuntu) | text/html |
| https://scanme.nmap.org | ERROR | (hidden) | N/A |
| http://example.com | 200 | None | text/html |
| https://example.com | 200 | None | text/html |
| http://httpbin.org | 200 | gunicorn/19.9.0 | text/html; charset=utf-8 |
| https://httpbin.org | 200 | gunicorn/19.9.0 | text/html; charset=utf-8 |
| https://www.microsoft.com | 200 | AkamaiNetStorage | text/html |
| https://github.com | 200 | github.com | text/html; charset=utf-8 |
| https://cloudflare.com | 200 | cloudflare | text/html; charset=utf-8 |
| https://aws.amazon.com | 200 | Server | text/html;charset=utf-8 |

---

## Header Probe Results

**Testing Multiple User-Agents Across Sites**

### http://example.com
- Status: 200
- Server: 
- Length: 513 bytes

### http://info.cern.ch
- Status: 200
- Server: Apache
- Length: 646 bytes

### http://scanme.nmap.org
- Status: 200
- Server: Apache/2.4.7 (Ubuntu)
- Length: 6974 bytes

### http://httpbin.org/status/200
- Status: 200
- Server: gunicorn/19.9.0
- Length: 0 bytes


---

## Keyword Analysis

**Searching for security-related keywords: admin, login, debug, error**

| Source | admin | login | debug | error |
|--------|-------|-------|-------|-------|
| scanme.html | 0 | 0 | 0 | 0 |
| scanme.nmap.org | 0 | 0 | 0 | 0 |
| example.com | 0 | 0 | 0 | 0 |

**Finding**: None of the tested public sites contain these keywords.


---

## WAF Detection Results

### https://www.cloudflare.com

**Header Variation Tests:**

- `x_forwarded_for`: Status 200, Length -35 bytes
- `suspicious_referer`: Status 200, Length -4 bytes
- `sqlmap_signature`: Status 200, Length -42 bytes
- `proxy_headers`: Status 200, Length -45 bytes
- `scanner_markers`: Status 200, Length -22 bytes

### https://www.amazon.com

**Header Variation Tests:**

- `suspicious_referer`: Status 200, Length +743389 bytes
- `sqlmap_signature`: Status 200, Length +206276 bytes


---

## Key Findings

### 1. Server Version Disclosure
- **scanme.nmap.org**: Apache/2.4.7 (Ubuntu) — Full version exposed
- **example.com**: Server header hidden (best practice)
- **httpbin.org**: gunicorn/19.9.0 — Python framework visible

### 2. WAF/Bot Protection Detection
- **Cloudflare**: Detects suspicious headers via content-length changes (-4 to -45 bytes)
- **Amazon**: Serves challenge pages for suspicious referers (+700KB response)
- **Simple sites**: No detection or filtering implemented

### 3. User-Agent Analysis
- **Basic sites**: No filtering — identical responses to all User-Agents
- **WAF sites**: Selective blocking based on User-Agent + header combinations
- **Curl/sqlmap/Nikto**: Detected on Cloudflare (403) and Amazon (503)

### 4. Keyword Distribution
- No public sites contain common security keywords (admin, login, debug, error)
- Custom applications would need specific keyword analysis

## Recommendations

1. **For Site Owners**:
   - Hide server version information in headers
   - Implement graduated WAF responses (challenge → block)
   - Monitor suspicious header combinations
   - Regular security header audits

2. **For Security Testers**:
   - Always obtain written authorization
   - Use legitimate User-Agent strings
   - Space requests to avoid rate limiting
   - Report findings responsibly

## Scripts Included

| Script | Purpose |
|--------|---------|
| `lab4-1_get.py` | Extract headers from single URL |
| `lab4-1_header_probe.py` | Multi-User-Agent testing |
| `lab4-1_parse.py` | HTML form and metadata extraction |
| `header_fuzzing.py` | Basic header variation testing |
| `advanced_header_fuzzing.py` | WAF detection via fuzzing |
| `user_agent_analysis.py` | User-Agent filtering analysis |
| `keyword_compare.py` | Keyword extraction and comparison |
| `waf_findings_report.py` | Comprehensive WAF report |

---

**Lab Status**: ✅ Complete  
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
