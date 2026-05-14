import urllib.request, json

BASE = "https://intellitrack-backend-gue5.onrender.com"

def req(method, path, body=None, token=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        resp = urllib.request.urlopen(r)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())

users = [
    {"name": "Arjun Sharma", "email": "arjun@intellidemo.com", "password": "Demo1234!", "id": 11},
    {"name": "Priya Mehta",  "email": "priya@intellidemo.com", "password": "Demo1234!", "id": 12},
    {"name": "Rohan Verma",  "email": "rohan@intellidemo.com", "password": "Demo1234!", "id": 13},
    {"name": "Sneha Iyer",   "email": "sneha@intellidemo.com", "password": "Demo1234!", "id": 14},
    {"name": "Karan Patel",  "email": "karan@intellidemo.com", "password": "Demo1234!", "id": 15},
    {"name": "Divya Nair",   "email": "divya@intellidemo.com", "password": "Demo1234!", "id": 16},
]
tokens = {}
for u in users:
    r = req("POST", "/auth/login", {"email": u["email"], "password": u["password"]})
    tokens[u["id"]] = r.get("access_token", "")

admin_token = tokens[11]

print("Demo fix seed complete!")
