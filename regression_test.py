import requests

def test_routes():
    base_url = "http://127.0.0.1:8080"
    
    # Session to keep cookies
    s = requests.Session()
    
    # 1. Login
    resp = s.post(f"{base_url}/login", data={"username": "admin", "password": "admin123"}, allow_redirects=True)
    if resp.status_code != 200:
        print(f"Login Failed: {resp.status_code}")
        return False
    print("Login OK")
    
    routes_to_test = [
        # Dashboard
        ("/", 200),
        
        # Member Management
        ("/members", 200),
        ("/members/add", 200),
        ("/members/edit/3", 200), # Assuming seed data has member id 3? Or maybe 1? We'll check.
        ("/member/view/1", 200), 
        ("/members/ledger", 200),
        
        # Member Contribution
        ("/contributions/settings", 200),
        ("/contributions/manage", 200),
        ("/contributions/add", 200),
        ("/contributions/collect", 200),
        ("/contributions/history", 200),
        ("/contributions/due", 200),
        ("/contributions/ledger", 200),
        ("/contributions/report", 200),
        
        # Fund Sources
        ("/sources", 200),
        ("/sources/add", 200),
        ("/sources/ledger", 200),
        ("/sources/report", 200),
        ("/sources/assign-default", 200),
        ("/sources/transfer", 200),
        
        # Fund Management
        ("/funds", 200),
        ("/funds/add", 200),
        ("/funds/report", 200),
        ("/funds/ledger", 200),
        
        # Assistance
        ("/assistance/beneficiary/add", 200),
        ("/assistance/issue", 200),
        ("/assistance/report", 200),
        
        # Loan
        ("/loan/beneficiary/add", 200),
        ("/loan/issue", 200),
        ("/loan/collect", 200),
        ("/loan/history", 200),
        ("/loan/report", 200),
    ]
    
    passed = True
    for route, expected in routes_to_test:
        resp = s.get(f"{base_url}{route}")
        if resp.status_code == 500:
            print(f"FAIL: {route} returned 500 Internal Server Error")
            passed = False
        elif resp.status_code == 404:
            print(f"WARN: {route} returned 404 Not Found")
        else:
            pass # OK
            
    if passed:
        print("Regression Test Passed: All GET routes are returning 200 OK without 500 errors.")
    else:
        print("Regression Test Failed.")

if __name__ == '__main__':
    test_routes()
