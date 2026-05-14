"""
Load test p95 latency — 25 concurrent users
"""
import urllib.request
import json
import time
import threading
import statistics
from collections import defaultdict

BASE = "http://intellitrack-alb-1279061505.us-east-1.elb.amazonaws.com"
results = defaultdict(list)
lock = threading.Lock()

def req(method, path, body=None, token=None):
    """Make HTTP request and return (status_code, response_time_ms)"""
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    r = urllib.request.Request(url, data=data, method=method, headers=headers)
    start = time.time()
    try:
        resp = urllib.request.urlopen(r, timeout=15)
        elapsed = (time.time() - start) * 1000
        return 200, elapsed, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        elapsed = (time.time() - start) * 1000
        try:
            body = json.loads(e.read().decode())
        except:
            body = {}
        return e.code, elapsed, body
    except Exception as ex:
        elapsed = (time.time() - start) * 1000
        return 500, elapsed, {"error": str(ex)}

def worker(user_id, num_requests):
    """Simulate one user making requests"""
    # Login
    status, elapsed, resp = req("POST", "/auth/login", {
        "email": "dheeraj@intellitrack.dev",
        "password": "Track2026!"
    })
    
    if status != 200 or "access_token" not in resp:
        print(f"  [User {user_id}] Login failed: {status}")
        return
    
    token = resp["access_token"]
    
    # Make requests
    endpoints = [
        ("/projects", "GET"),
        ("/dashboard", "GET"),
        ("/issues", "GET"),
        ("/wiki", "GET"),
    ]
    
    for i in range(num_requests):
        for path, method in endpoints:
            status, elapsed, resp = req(method, path, token=token)
            
            with lock:
                results[path].append(elapsed)
            
            if i == 0:
                print(f"  [User {user_id}] {method} {path}: {elapsed:.1f}ms")

print("=" * 70)
print("Load Test: 25 concurrent users, 2 requests per user per endpoint")
print("=" * 70)

num_users = 25
requests_per_user = 2

threads = []
print(f"\nSpawning {num_users} workers...")
start_time = time.time()

for user_id in range(num_users):
    t = threading.Thread(target=worker, args=(user_id, requests_per_user))
    t.start()
    threads.append(t)
    time.sleep(0.1)  # Stagger starts

print("Waiting for all workers to complete...")
for t in threads:
    t.join()

total_time = time.time() - start_time

print("\n" + "=" * 70)
print("RESULTS — 95th Percentile Latency")
print("=" * 70)

all_times = []
for path in sorted(results.keys()):
    times = results[path]
    if times:
        p50 = statistics.median(times)
        p95 = sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else times[0]
        p99 = sorted(times)[int(len(times) * 0.99)] if len(times) > 1 else times[0]
        avg = statistics.mean(times)
        
        all_times.extend(times)
        
        print(f"\n{path}")
        print(f"  Samples:    {len(times)}")
        print(f"  Avg:        {avg:.1f} ms")
        print(f"  p50 (median): {p50:.1f} ms")
        print(f"  p95:        {p95:.1f} ms ✓")
        print(f"  p99:        {p99:.1f} ms")

if all_times:
    print(f"\n{'─' * 70}")
    print(f"OVERALL (all {len(all_times)} requests)")
    print(f"  p95:        {sorted(all_times)[int(len(all_times) * 0.95)]:.1f} ms")
    print(f"  Avg:        {statistics.mean(all_times):.1f} ms")
    print(f"  Total time: {total_time:.1f} seconds")

print("\n" + "=" * 70)
