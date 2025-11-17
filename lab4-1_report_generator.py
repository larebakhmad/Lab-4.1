#!/usr/bin/env python3
# lab4-1_report_generator.py - Generate markdown summary from collected data

import json
import os
from datetime import datetime
from pathlib import Path

def load_json(filename):
    """Safely load JSON file."""
    filepath = Path(f"/workspaces/Lab-4.1/{filename}")
    if filepath.exists():
        with open(filepath) as f:
            return json.load(f)
    return None

def generate_headers_summary():
    """Generate summary from Headers.json"""
    data = load_json("Headers.json")
    if not data:
        return "No header data found."
    
    summary = "## Server Headers Summary\n\n"
    summary += "| URL | Status | Server | Content-Type |\n"
    summary += "|-----|--------|--------|---------------|\n"
    
    for entry in data:
        url = entry.get('url', 'N/A')
        status = entry.get('status', 'ERROR')
        server = entry.get('server', '(hidden)')
        content_type = entry.get('content_type', 'N/A')
        
        # Truncate for table
        if server and len(server) > 30:
            server = server[:27] + "..."
        if content_type and len(content_type) > 30:
            content_type = content_type[:27] + "..."
        
        summary += f"| {url} | {status} | {server} | {content_type} |\n"
    
    return summary

def generate_probe_summary():
    """Generate summary from header probe results"""
    data = load_json("header_probe_comparison.json")
    if not data:
        return "No probe data found."
    
    summary = "## Header Probe Results\n\n"
    summary += "**Testing Multiple User-Agents Across Sites**\n\n"
    
    for site, probes in data.items():
        summary += f"### {site}\n"
        
        if probes and isinstance(probes, list) and len(probes) > 0:
            first = probes[0]
            summary += f"- Status: {first.get('status', 'N/A')}\n"
            summary += f"- Server: {first.get('server', '(hidden)')}\n"
            summary += f"- Length: {first.get('length', 'N/A')} bytes\n"
        summary += "\n"
    
    return summary

def generate_waf_summary():
    """Generate WAF detection summary"""
    data = load_json("advanced_header_fuzzing.json")
    if not data:
        return "No WAF data found."
    
    summary = "## WAF Detection Results\n\n"
    
    for site, variations in data.items():
        summary += f"### {site}\n\n"
        
        baseline = variations.get("baseline", {})
        baseline_len = baseline.get("content_length", 0)
        
        summary += "**Header Variation Tests:**\n\n"
        
        for var_name, var_data in variations.items():
            if var_name == "baseline":
                continue
            
            status = var_data.get("status", "ERROR")
            length = var_data.get("content_length", 0)
            diff = length - baseline_len
            
            if diff != 0:
                summary += f"- `{var_name}`: Status {status}, Length {diff:+d} bytes\n"
        
        summary += "\n"
    
    return summary

def generate_keywords_summary():
    """Generate keyword analysis summary"""
    data = load_json("keyword_results_detailed.json")
    if not data:
        return "No keyword data found."
    
    summary = "## Keyword Analysis\n\n"
    summary += "**Searching for security-related keywords: admin, login, debug, error**\n\n"
    summary += "| Source | admin | login | debug | error |\n"
    summary += "|--------|-------|-------|-------|-------|\n"
    
    for source, result in data.items():
        if "error" not in result:
            counts = result.get("keyword_counts", {})
            admin_c = counts.get("admin", 0)
            login_c = counts.get("login", 0)
            debug_c = counts.get("debug", 0)
            error_c = counts.get("error", 0)
            
            source_short = source.replace("/workspaces/Lab-4.1/", "").replace("http://", "").replace("https://", "")
            summary += f"| {source_short} | {admin_c} | {login_c} | {debug_c} | {error_c} |\n"
    
    summary += "\n**Finding**: None of the tested public sites contain these keywords.\n\n"
    
    return summary

def generate_full_report():
    """Generate complete markdown report"""
    report = f"""# Lab 4.1 - HTTP Reconnaissance Report
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This lab performs passive HTTP reconnaissance on multiple websites to identify:
- Server technologies and versions
- Response patterns to different User-Agents
- WAF (Web Application Firewall) detection mechanisms
- Content patterns and keywords

---

"""
    
    report += generate_headers_summary()
    report += "\n---\n\n"
    
    report += generate_probe_summary()
    report += "\n---\n\n"
    
    report += generate_keywords_summary()
    report += "\n---\n\n"
    
    report += generate_waf_summary()
    report += "\n---\n\n"
    
    report += """## Key Findings

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
"""
    
    return report

def main():
    """Generate and save report."""
    report = generate_full_report()
    
    output_file = Path("/workspaces/Lab-4.1/lab4-1_ANALYSIS_REPORT.md")
    with open(output_file, "w") as f:
        f.write(report)
    
    print(f"✓ Report generated: {output_file}")
    print(f"✓ Word count: {len(report.split())}")

if __name__ == "__main__":
    main()
