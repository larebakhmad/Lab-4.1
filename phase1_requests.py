import requests
r = requests.get("http://scanme.nmap.org", timeout=5)
print("Status:", r.status_code)
print("Final URL:", r.url)
print("Server header:", r.headers.get("Server"))
print("Content-Type:", r.headers.get("Content-Type"))
print("First 200 chars of body:\\n", r.text[:200].replace('\n','\\n'))