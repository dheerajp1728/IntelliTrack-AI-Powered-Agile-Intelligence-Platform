"""
Demo seed script — creates a realistic IntelliTrack demo on the live Render deployment.
Run: python seed_demo.py
"""

import urllib.request
import json
import sys

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
        err = e.read().decode()
        print(f"  [WARN] {method} {path} → {e.code}: {err[:120]}")
        try:
            return json.loads(err)
        except:
            return {}


print("=" * 60)
print("  IntelliTrack Demo Seed")
print("=" * 60)

# ── 1. Register users ─────────────────────────────────────────────────────────
print("\n[1/7] Creating demo users...")
users_data = [
    {"name": "Arjun Sharma",  "email": "arjun@intellidemo.com",  "password": "Demo1234!", "role": "Admin"},
    {"name": "Priya Mehta",   "email": "priya@intellidemo.com",  "password": "Demo1234!", "role": "Scrum Master"},
    {"name": "Rohan Verma",   "email": "rohan@intellidemo.com",  "password": "Demo1234!", "role": "Developer"},
    {"name": "Sneha Iyer",    "email": "sneha@intellidemo.com",  "password": "Demo1234!", "role": "Developer"},
    {"name": "Karan Patel",   "email": "karan@intellidemo.com",  "password": "Demo1234!", "role": "Developer"},
    {"name": "Divya Nair",    "email": "divya@intellidemo.com",  "password": "Demo1234!", "role": "QA"},
]

tokens = {}
user_ids = {}

for u in users_data:
    result = req("POST", "/auth/register", u)
    if "access_token" in result:
        tokens[u["email"]] = result["access_token"]
        user_ids[u["name"]] = result["user_id"]
        print(f"  ✅ Registered: {u['name']} (ID {result['user_id']})")
    elif "access_token" not in result:
        # already exists, try login
        result = req("POST", "/auth/login", {"email": u["email"], "password": u["password"]})
        if "access_token" in result:
            tokens[u["email"]] = result["access_token"]
            user_ids[u["name"]] = result["user_id"]
            print(f"  ℹ️  Already exists, logged in: {u['name']} (ID {result['user_id']})")

admin_token = tokens.get("arjun@intellidemo.com")
arjun_id    = user_ids.get("Arjun Sharma")
priya_id    = user_ids.get("Priya Mehta")
rohan_id    = user_ids.get("Rohan Verma")
sneha_id    = user_ids.get("Sneha Iyer")
karan_id    = user_ids.get("Karan Patel")
divya_id    = user_ids.get("Divya Nair")

if not admin_token:
    print("\n❌ Could not get admin token. Aborting.")
    sys.exit(1)

print("\n✅ Demo seed complete!")
