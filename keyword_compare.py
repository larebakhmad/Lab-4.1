#!/usr/bin/env python3
# keyword_compare.py - Compare keyword counts across different sites

import requests
from bs4 import BeautifulSoup
import json
from collections import defaultdict

# Keywords to search for
keywords = ["admin", "login", "debug", "error"]

# Sites to analyze
sites = [
    "http://scanme.nmap.org",
    "http://example.com",
    "http://info.cern.ch",  # Historical website
]

results = {}

print("=" * 70)
print("KEYWORD COUNT COMPARISON ACROSS SITES")
print("=" * 70)
print(f"\nKeywords being searched: {keywords}\n")

for url in sites:
    print(f"\nFetching: {url}")
    print("-" * 70)
    
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Extract text and convert to lowercase
        text = soup.get_text(separator=" ").lower()
        
        # Count keyword occurrences
        kw_counts = {k: text.count(k) for k in keywords}
        
        # Store results
        results[url] = {
            "status": r.status_code,
            "content_length": len(r.text),
            "text_length": len(text),
            "keyword_counts": kw_counts
        }
        
        # Display results for this site
        print(f"Status Code: {r.status_code}")
        print(f"Content Length: {len(r.text)} characters")
        print(f"Text Length (extracted): {len(text)} characters")
        print(f"Keyword Counts:")
        for kw, count in kw_counts.items():
            print(f"  - {kw:10} : {count:4} occurrences")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
        results[url] = {"error": str(e)}

# Summary comparison
print("\n" + "=" * 70)
print("SUMMARY COMPARISON")
print("=" * 70)

# Create comparison table
print(f"\n{'URL':<40}", end="")
for kw in keywords:
    print(f"{kw:>10}", end="")
print()
print("-" * (40 + len(keywords) * 10))

for url, data in results.items():
    if "error" not in data:
        print(f"{url:<40}", end="")
        for kw in keywords:
            count = data["keyword_counts"].get(kw, 0)
            print(f"{count:>10}", end="")
        print()

# Find which keyword is most common
print("\n" + "=" * 70)
print("KEYWORD FREQUENCY ANALYSIS")
print("=" * 70)

total_counts = defaultdict(int)
for url, data in results.items():
    if "error" not in data:
        for kw, count in data["keyword_counts"].items():
            total_counts[kw] += count

print("\nTotal occurrences across all sites:")
for kw in keywords:
    print(f"  {kw:10}: {total_counts[kw]:4} occurrences")

if total_counts:
    most_common = max(total_counts, key=total_counts.get)
    print(f"\nMost common keyword: '{most_common}' ({total_counts[most_common]} occurrences)")

# Save detailed results to JSON
output_file = "/workspaces/Lab-4.1/keyword_results.json"
with open(output_file, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Detailed results saved to: {output_file}")
