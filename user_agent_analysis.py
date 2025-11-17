#!/usr/bin/env python3
# user_agent_analysis.py - Analyze if servers respond differently to specific user agents

import json
from tabulate import tabulate

# Load the probe data
with open("/workspaces/Lab-4.1/header_probe_comparison.json") as f:
    data = json.load(f)

# User agents to focus on
target_uas = ["curl/7.68.0", "sqlmap/1.5.4", "Nikto/2.1.6"]

print("=" * 90)
print("USER-AGENT RESPONSE ANALYSIS: curl vs sqlmap vs Nikto")
print("=" * 90)

for site, probes in data.items():
    print(f"\n{'='*90}")
    print(f"Site: {site}")
    print(f"{'='*90}\n")
    
    # Extract data for target user agents
    rows = []
    for probe in probes:
        if probe.get('ua') in target_uas:
            ua_name = probe['ua'].split('/')[0]
            rows.append({
                'User-Agent': ua_name,
                'Status': probe.get('status', 'ERROR'),
                'Server': probe.get('server', '(None)'),
                'Length': probe.get('length', 'ERROR'),
                'Content-Type': probe.get('content_type', 'N/A'),
            })
    
    if rows:
        print(tabulate(rows, headers="keys", tablefmt="grid"))
    
    # Check for differences
    statuses = [p.get('status') for p in probes if p.get('ua') in target_uas]
    lengths = [p.get('length') for p in probes if p.get('ua') in target_uas]
    servers = [p.get('server') for p in probes if p.get('ua') in target_uas]
    
    print("\nAnalysis:")
    
    if len(set(statuses)) == 1:
        print(f"  ✓ Status Code: SAME ({statuses[0]}) - No differentiation")
    else:
        print(f"  ⚠️  Status Code: VARIES - {dict(zip(['curl', 'sqlmap', 'Nikto'], statuses))}")
    
    if len(set(lengths)) == 1:
        print(f"  ✓ Content Length: SAME ({lengths[0]} bytes) - No differentiation")
    else:
        print(f"  ⚠️  Content Length: VARIES - {dict(zip(['curl', 'sqlmap', 'Nikto'], lengths))}")
    
    if len(set(servers)) == 1:
        print(f"  ✓ Server Header: SAME ('{servers[0]}') - No differentiation")
    else:
        print(f"  ⚠️  Server Header: VARIES - {dict(zip(['curl', 'sqlmap', 'Nikto'], servers))}")

# Summary comparison
print(f"\n\n{'='*90}")
print("SUMMARY")
print(f"{'='*90}\n")

all_respond_same = True
for site, probes in data.items():
    target_probes = [p for p in probes if p.get('ua') in target_uas]
    statuses = [p.get('status') for p in target_probes]
    lengths = [p.get('length') for p in target_probes]
    
    if len(set(statuses)) > 1 or len(set(lengths)) > 1:
        all_respond_same = False
        break

if all_respond_same:
    print("✓ CONCLUSION: Servers respond IDENTICALLY to curl, sqlmap, and Nikto user agents")
    print("  → No user-agent filtering or fingerprinting detected")
    print("  → These tools would NOT be blocked based on User-Agent header alone")
else:
    print("⚠️  CONCLUSION: Servers respond DIFFERENTLY to at least one user agent")
    print("  → Some servers may have user-agent filtering")
    print("  → These tools could be detected/blocked based on User-Agent header")
