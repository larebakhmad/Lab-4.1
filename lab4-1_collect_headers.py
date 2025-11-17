#!/usr/bin/env python3
# lab4-1_collect_headers.py - Collect and organize HTTP headers from multiple targets

import requests
import json
import sys
from pathlib import Path
from datetime import datetime

def collect_headers(urls, output_file="Headers.json"):
    """Collect headers from multiple URLs and save to JSON."""
    
    results = []
    
    print("=" * 80)
    print("HTTP Header Collection")
    print("=" * 80)
    
    for url in urls:
        print(f"\nFetching: {url}")
        
        try:
            # Try both HTTP and HTTPS
            for scheme in ["http://", "https://"]:
                if not url.startswith(("http://", "https://")):
                    test_url = scheme + url
                else:
                    test_url = url
                
                try:
                    r = requests.get(test_url, timeout=5, allow_redirects=True, verify=False)
                    
                    result = {
                        "url": test_url,
                        "status": r.status_code,
                        "final_url": r.url,
                        "server": r.headers.get("Server"),
                        "content_type": r.headers.get("Content-Type"),
                        "content_length": r.headers.get("Content-Length"),
                        "timestamp": datetime.now().isoformat(),
                        "headers": dict(r.headers)
                    }
                    
                    results.append(result)
                    
                    print(f"  ✓ {test_url}")
                    print(f"    Status: {r.status_code}")
                    print(f"    Server: {r.headers.get('Server', '(hidden)')}")
                    print(f"    Content-Type: {r.headers.get('Content-Type', 'N/A')}")
                    
                except requests.exceptions.ConnectionError:
                    pass  # Try next scheme
                except requests.exceptions.Timeout:
                    pass  # Try next scheme
                except Exception:
                    pass  # Try next scheme
            
            if not any(result.get("url") == url for result in results):
                results.append({
                    "url": url,
                    "error": "Could not reach URL"
                })
        
        except Exception as e:
            results.append({
                "url": url,
                "error": str(e)
            })
    
    # Save results
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Headers saved to: {output_file}")
    return results

def main():
    """Main entry point."""
    
    # Default targets
    default_urls = [
        "http://scanme.nmap.org",
        "https://scanme.nmap.org",
        "http://example.com",
        "https://example.com",
        "http://httpbin.org",
        "https://httpbin.org",
        "http://info.cern.ch",
        "https://info.cern.ch",
    ]
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        # Custom URLs provided
        urls = sys.argv[1:]
        output = "custom_headers.json"
    else:
        # Use defaults
        urls = default_urls
        output = "Headers.json"
    
    # Collect headers
    results = collect_headers(urls, output)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in results if "error" not in r)
    failed = sum(1 for r in results if "error" in r)
    
    print(f"\nSuccessful: {successful}")
    print(f"Failed: {failed}")
    
    # Server statistics
    servers = {}
    for result in results:
        if "error" not in result and result.get("server"):
            server = result["server"]
            servers[server] = servers.get(server, 0) + 1
    
    if servers:
        print("\nServers detected:")
        for server, count in sorted(servers.items()):
            print(f"  {server}: {count} site(s)")

if __name__ == "__main__":
    main()
