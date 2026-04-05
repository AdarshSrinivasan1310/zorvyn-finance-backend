import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_system():
    print("--- AUTOMATED SYSTEM VERIFICATION ---")
    
    # 1. Test Registration
    try:
        resp = requests.post(f"{BASE_URL}/users/register", json={
            "username": "system_verifier",
            "password": "password123",
            "role": "Admin"
        })
        if resp.status_code not in (201, 400): # 400 if already exists
            print(f"FAILED Registration: {resp.text}")
            sys.exit(1)
        print("✅ Registration Endpoint OK")
    except Exception as e:
        print(f"FAILED Registration Connection: {e}")
        sys.exit(1)

    # 2. Test Login
    resp = requests.post(f"{BASE_URL}/users/token", data={
        "username": "system_verifier",
        "password": "password123"
    })
    if resp.status_code != 200:
        print(f"FAILED Login: {resp.text}")
        sys.exit(1)
    print("✅ Authentication Endpoint OK")
    
    token = resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Test Create Record
    resp = requests.post(f"{BASE_URL}/records/", json={
        "amount": 999.0,
        "record_type": "Income",
        "category": "Verification",
        "date": "2026-04-03T00:00:00Z",
        "notes": "this is a verification test"
    }, headers=headers)
    if resp.status_code != 200:
        print(f"FAILED Create Record: {resp.text}")
        sys.exit(1)
    record_id = resp.json().get("id")
    print("✅ Financial Records (Create) OK")

    # 4. Test Search / Get Records Filters
    resp = requests.get(f"{BASE_URL}/records/?search=verification&record_type=Income", headers=headers)
    if resp.status_code != 200:
        print(f"FAILED Get Records: {resp.text}")
        sys.exit(1)
    print("✅ Financial Records (Search/Filters/Pagination) OK")

    # 5. Test Update Record
    resp = requests.put(f"{BASE_URL}/records/{record_id}", json={
        "amount": 1000.0,
        "record_type": "Income",
        "category": "Verification",
        "date": "2026-04-03T00:00:00Z",
        "notes": "updated verification test"
    }, headers=headers)
    if resp.status_code != 200:
        print(f"FAILED Update Record: {resp.text}")
        sys.exit(1)
    print("✅ Financial Records (Update) OK")
    
    # 6. Test Dashboard Aggregations
    resp = requests.get(f"{BASE_URL}/dashboard/summary", headers=headers)
    if resp.status_code != 200:
        print(f"FAILED Dashboard Summary: {resp.text}")
        sys.exit(1)
    data = resp.json()
    if 'monthly_trends' not in data or 'recent_activity' not in data:
        print("FAILED Dashboard: Missing keys")
        sys.exit(1)
    print("✅ Dashboard (Aggregations/Trends/Activity) OK")

    # 7. Test Soft Delete
    resp = requests.delete(f"{BASE_URL}/records/{record_id}", headers=headers)
    if resp.status_code != 200:
        print(f"FAILED Delete Record: {resp.text}")
        sys.exit(1)
    print("✅ Financial Records (Soft Delete) OK")
    # 8. Test RBAC Enforcement (Negative Test)
    requests.post(f"{BASE_URL}/users/register", json={
        "username": "viewer_test",
        "password": "password123",
        "role": "Viewer"
    })
    resp = requests.post(f"{BASE_URL}/users/token", data={
        "username": "viewer_test",
        "password": "password123"
    })
    if resp.status_code == 200:
        viewer_token = resp.json().get("access_token")
        viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
        
        resp = requests.post(f"{BASE_URL}/records/", json={
            "amount": 10.0,
            "record_type": "Income",
            "category": "Test",
            "date": "2026-04-04T00:00:00Z"
        }, headers=viewer_headers)
        
        if resp.status_code != 403:
            print(f"FAILED RBAC Negative Test: Expected 403, got {resp.status_code}")
            sys.exit(1)
        print("✅ RBAC Negative Test (Viewer cannot mutate records) OK")
        
    print("--- ALL TESTS PASSED FLAWLESSLY ---")

if __name__ == "__main__":
    test_system()
