#!/usr/bin/env python3
# keyword_compare_local.py - Compare keyword counts from local HTML files and URLs

from bs4 import BeautifulSoup
import json
from collections import defaultdict
import requests
import os

# Keywords to search for
keywords = ["admin", "login", "debug", "error"]

# Local HTML files to analyze
local_files = [
    "/workspaces/Lab-4.1/scanme.html",
]

# Remote sites to analyze
remote_sites = [
    "http://scanme.nmap.org",
    "http://example.com",
]

results = {}

print("=" * 70)
print("KEYWORD COUNT COMPARISON - LOCAL FILES & REMOTE SITES")
print("=" * 70)
print(f"\nKeywords being searched: {keywords}\n")

# Analyze local files
print("LOCAL FILES")
print("-" * 70)

for filepath in local_files:
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        continue
    
    print(f"\nAnalyzing: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text(separator=" ").lower()
        
        kw_counts = {k: text.count(k) for k in keywords}
        
        results[filepath] = {
            "type": "local_file",
            "content_length": len(content),
            "text_length": len(text),
            "keyword_counts": kw_counts
        }
        
        print(f"File Size: {len(content)} characters")
        print(f"Extracted Text Length: {len(text)} characters")
        print(f"Keyword Counts:")
        for kw, count in kw_counts.items():
            print(f"  - {kw:10} : {count:4} occurrences")
            
    except Exception as e:
        print(f"❌ Error analyzing {filepath}: {e}")
        results[filepath] = {"error": str(e)}

# Analyze remote sites
print("\n\nREMOTE SITES")
print("-" * 70)

for url in remote_sites:
    print(f"\nFetching: {url}")
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        
        text = soup.get_text(separator=" ").lower()
        kw_counts = {k: text.count(k) for k in keywords}
        
        results[url] = {
            "type": "remote_site",
            "status": r.status_code,
            "content_length": len(r.text),
            "text_length": len(text),
            "keyword_counts": kw_counts
        }
        
        print(f"Status Code: {r.status_code}")
        print(f"Content Length: {len(r.text)} characters")
        print(f"Extracted Text Length: {len(text)} characters")
        print(f"Keyword Counts:")
        for kw, count in kw_counts.items():
            print(f"  - {kw:10} : {count:4} occurrences")
            
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        results[url] = {"error": str(e)}

# Summary comparison
print("\n" + "=" * 70)
print("SUMMARY COMPARISON TABLE")
print("=" * 70)

print(f"\n{'Source':<45}", end="")
for kw in keywords:
    print(f"{kw:>10}", end="")
print()
print("-" * (45 + len(keywords) * 10))

for source, data in results.items():
    if "error" not in data:
        display_name = source.replace('/workspaces/Lab-4.1/', '')
        print(f"{display_name:<45}", end="")
        for kw in keywords:
            count = data["keyword_counts"].get(kw, 0)
            print(f"{count:>10}", end="")
        print()

# Keyword frequency analysis
print("\n" + "=" * 70)
print("KEYWORD FREQUENCY ANALYSIS")
print("=" * 70)

total_counts = defaultdict(int)
for source, data in results.items():
    if "error" not in data:
        for kw, count in data["keyword_counts"].items():
            total_counts[kw] += count

print("\nTotal occurrences across all sources:")
for kw in keywords:
    count = total_counts[kw]
    print(f"  {kw:10}: {count:4} occurrences", end="")
    if count > 0:
        print(f" ({'Found on:' if count > 0 else ''})", end="")
    print()

# Show which sources had keywords
print("\nKeyword locations:")
for kw in keywords:
    found_in = []
    for source, data in results.items():
        if "error" not in data and data["keyword_counts"].get(kw, 0) > 0:
            display_name = source.replace('/workspaces/Lab-4.1/', '')
            found_in.append(f"{display_name} ({data['keyword_counts'][kw]}x)")
    
    if found_in:
        print(f"  '{kw}': {', '.join(found_in)}")
    else:
        print(f"  '{kw}': Not found in any source")

# Save detailed results to JSON
output_file = "/workspaces/Lab-4.1/keyword_results_detailed.json"
with open(output_file, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Detailed results saved to: {output_file}")
