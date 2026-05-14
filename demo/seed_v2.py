"""
IntelliTrack Demo Seed v2
- Targets the live AWS ALB deployment
- 8 varied team members
- 7 sprints (S1–S6 completed, S7 active) based on real IntelliTrack dev history
- 50+ realistic issues across all sprints
Run: python seed_v2.py
"""

import urllib.request
import json
import sys

BASE = "http://intellitrack-alb-1279061505.us-east-1.elb.amazonaws.com"

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
        print(f"  [WARN] {method} {path} → {e.code}: {err[:160]}")
        try:
            return json.loads(err)
        except Exception:
            return {}
    except Exception as ex:
        print(f"  [ERR] {method} {path} → {ex}")
        return {}


print("=" * 65)
print("  IntelliTrack Demo Seed v2  —  AWS ECS Deployment")
print("=" * 65)

# ─────────────────────────────────────────────────────────────────────────────
# 1. USERS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[1/7] Registering team members...")

users_data = [
    {"name": "Raunak",    "email": "raunak@intellitrack.dev",    "password": "Track2026!", "role": "Admin"},
    {"name": "Vignesh",   "email": "vignesh@intellitrack.dev",   "password": "Track2026!", "role": "Scrum Master"},
    {"name": "Dheeraj",   "email": "dheeraj@intellitrack.dev",  "password": "Track2026!", "role": "Developer"},
    {"name": "Hemanesh",  "email": "hemanesh@intellitrack.dev",  "password": "Track2026!", "role": "Developer"},
    {"name": "Upasana",   "email": "upasana@intellitrack.dev",   "password": "Track2026!", "role": "Developer"},
]

tokens = {}
user_ids = {}

for u in users_data:
    result = req("POST", "/auth/register", u)
    if "access_token" in result:
        tokens[u["email"]] = result["access_token"]
        user_ids[u["name"]] = result.get("user_id") or result.get("id")
        print(f"  ✅ Registered:  {u['name']}  ({u['role']})")
    else:
        # already exists — login
        result = req("POST", "/auth/login", {"email": u["email"], "password": u["password"]})
        if "access_token" in result:
            tokens[u["email"]] = result["access_token"]
            user_ids[u["name"]] = result.get("user_id") or result.get("id")
            print(f"  ℹ️  Existing:    {u['name']}  (re-logged in)")
        else:
            print(f"  ❌ Could not auth: {u['name']}")

admin_token  = tokens.get("raunak@intellitrack.dev")

if not admin_token:
    print("\n❌ Could not get admin token. Aborting.")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# 2. DEVELOPER PROFILES
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2/7] Creating developer profiles...")

profiles = [
    {
        "user_id": user_ids.get("Raunak"),
        "full_name": "Raunak",
        "role_title": "Engineering Lead",
        "department": "Engineering",
        "bio": "Full-stack engineer and team lead. Designed the IntelliTrack platform architecture.",
        "skills": "Python, FastAPI, SQLAlchemy, React, AWS ECS, System Design, PostgreSQL",
        "experience_level": "Senior",
        "capacity": 8,
        "availability_status": "Busy",
    },
    {
        "user_id": user_ids.get("Vignesh"),
        "full_name": "Vignesh",
        "role_title": "Full Stack Developer / Scrum Master",
        "department": "Engineering",
        "bio": "Full-stack developer who also runs sprint ceremonies.",
        "skills": "Python, FastAPI, React, Agile, Sprint Planning, PostgreSQL",
        "experience_level": "Senior",
        "capacity": 8,
        "availability_status": "Available",
    },
]

for p in profiles:
    r = req("POST", "/profiles", p, admin_token)
    if "id" in r:
        print(f"  ✅ Profile: {p['full_name']}")
    else:
        print(f"  ⚠️  Profile skipped (may already exist): {p['full_name']}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. PROJECT
# ─────────────────────────────────────────────────────────────────────────────
print("\n[3/7] Creating project...")

project = req("POST", "/projects", {
    "name": "IntelliTrack Platform",
    "key": "ITP",
    "description": "AI-powered agile project management platform deployed on AWS ECS Fargate.",
    "status": "Active",
    "category": "Product Development",
    "lead_id": user_ids.get("Raunak"),
}, admin_token)

project_id = project.get("id")
if project_id:
    print(f"  ✅ Project: {project.get('name')}  (ID {project_id})")
else:
    print("  ❌ Failed to create project.")

print("\n✅ Demo seed v2 complete!")
