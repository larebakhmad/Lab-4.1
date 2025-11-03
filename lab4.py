import requests
r = requests.get("http://scanme.namp.org")
print(r.status_code)