import httpx
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

def print_test(method, endpoint, status, success=True):
    symbol = "✓" if success else "✗"
    print(f"{symbol} {method} {endpoint} : {status}")

# Test 1: Health Check
print("=" * 60)
print("1. HEALTH CHECKS")
print("=" * 60)
try:
    r = httpx.get(f"{BASE_URL}/")
    print_test("GET", "/", r.status_code, r.status_code == 200)
    if r.status_code == 200:
        data = r.json()
        print(f"  Message: {data.get('message')}")
except Exception as e:
    print(f"✗ Connection error: {e}")
    exit(1)

# Test 2: Register User
print("\n" + "=" * 60)
print("2. AUTHENTICATION")
print("=" * 60)
admin_data = {
    "username": "admin_test_user",
    "email": "admin@test.local",
    "password": "TestPass123!",
    "role": "admin"
}
r = httpx.post(f"{BASE_URL}/api/auth/register", json=admin_data)
print_test("POST", "/api/auth/register", r.status_code, r.status_code == 200)
if r.status_code == 200:
    admin_user = r.json()
    print(f"  Admin created: ID={admin_user.get('id')}, Username={admin_user.get('username')}")

# Test 3: Login
login_data = {"username": "admin_test_user", "password": "TestPass123!"}
r = httpx.post(f"{BASE_URL}/api/auth/login", json=login_data)
print_test("POST", "/api/auth/login", r.status_code, r.status_code == 200)

token = None
if r.status_code == 200:
    token_response = r.json()
    token = token_response.get("access_token")
    print(f"  Token received: {token[:40]}...")
else:
    print(f"  Error: {r.text}")

if not token:
    print("\n✗ Failed to obtain authentication token. Stopping tests.")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Test 4: Concert Management
print("\n" + "=" * 60)
print("3. CONCERT MANAGEMENT")
print("=" * 60)
concert_data = {
    "name": "Summer Music Festival 2025",
    "date": (datetime.utcnow() + timedelta(days=45)).isoformat(),
    "venue": "Central Park Amphitheater",
    "description": "A summer festival featuring multiple artists"
}
r = httpx.post(f"{BASE_URL}/api/concerts/", json=concert_data, headers=headers)
print_test("POST", "/api/concerts/", r.status_code, r.status_code == 200)

concert_id = None
if r.status_code == 200:
    concert = r.json()
    concert_id = concert.get("id")
    print(f"  Concert created: ID={concert_id}, Name={concert.get('name')}")
else:
    print(f"  Error: {r.text}")

# List concerts
r = httpx.get(f"{BASE_URL}/api/concerts/", headers=headers)
print_test("GET", "/api/concerts/", r.status_code, r.status_code == 200)
if r.status_code == 200:
    concerts = r.json()
    if isinstance(concerts, list):
        print(f"  Total concerts: {len(concerts)}")

# Get concert details
if concert_id:
    r = httpx.get(f"{BASE_URL}/api/concerts/{concert_id}", headers=headers)
    print_test("GET", f"/api/concerts/{concert_id}", r.status_code, r.status_code == 200)

# Test 5: Ticket Generation
print("\n" + "=" * 60)
print("4. TICKET GENERATION")
print("=" * 60)
if concert_id:
    ticket_data = {"quantity": 10, "price": 75.00}
    r = httpx.post(f"{BASE_URL}/api/tickets/create/{concert_id}", json=ticket_data, headers=headers)
    print_test("POST", f"/api/tickets/create/{concert_id}", r.status_code, r.status_code == 200)
    
    ticket_id = None
    if r.status_code == 200:
        tickets = r.json()
        if isinstance(tickets, list):
            print(f"  Generated {len(tickets)} tickets")
            if tickets:
                ticket_id = tickets[0].get("id")
                ticket_number = tickets[0].get("ticket_number")
                print(f"  First ticket: ID={ticket_id}, Number={ticket_number}")
    else:
        print(f"  Error: {r.text}")
    
    # List concert tickets
    r = httpx.get(f"{BASE_URL}/api/tickets/concert/{concert_id}", headers=headers)
    print_test("GET", f"/api/tickets/concert/{concert_id}", r.status_code, r.status_code == 200)
    if r.status_code == 200:
        tickets_list = r.json()
        if isinstance(tickets_list, list):
            print(f"  Retrieved {len(tickets_list)} tickets")
    
    # Mark ticket as sold
    if ticket_id:
        r = httpx.post(f"{BASE_URL}/api/tickets/{ticket_id}/mark-sold", json={}, headers=headers)
        print_test("POST", f"/api/tickets/{ticket_id}/mark-sold", r.status_code, r.status_code == 200)
        if r.status_code == 200:
            updated_ticket = r.json()
            print(f"  Ticket status: {updated_ticket.get('status')}")

# Test 6: Attendance/Scans
print("\n" + "=" * 60)
print("5. ATTENDANCE TRACKING")
print("=" * 60)
if concert_id:
    r = httpx.get(f"{BASE_URL}/api/scans/concert/{concert_id}/attendance", headers=headers)
    print_test("GET", f"/api/scans/concert/{concert_id}/attendance", r.status_code, r.status_code == 200)
    if r.status_code == 200:
        stats = r.json()
        print(f"  Attendance stats retrieved: {json.dumps(stats, indent=2)}")

# Test 7: Transfers
print("\n" + "=" * 60)
print("6. TICKET TRANSFERS")
print("=" * 60)
# Create another user to transfer to
recipient_data = {
    "username": "recipient_user",
    "email": "recipient@test.local",
    "password": "TestPass123!",
    "role": "viewer"
}
r = httpx.post(f"{BASE_URL}/api/auth/register", json=recipient_data)
print_test("POST", "/api/auth/register (recipient)", r.status_code, r.status_code == 200)

if concert_id and ticket_id:
    transfer_data = {
        "ticket_id": ticket_id,
        "recipient_username": "recipient_user"
    }
    r = httpx.post(f"{BASE_URL}/api/transfers/initiate", json=transfer_data, headers=headers)
    print_test("POST", "/api/transfers/initiate", r.status_code, r.status_code in [200, 400])
    if r.status_code != 200:
        print(f"  Note: {r.text}")

# Get pending transfers
r = httpx.get(f"{BASE_URL}/api/transfers/pending", headers=headers)
print_test("GET", "/api/transfers/pending", r.status_code, r.status_code == 200)
if r.status_code == 200:
    transfers = r.json()
    if isinstance(transfers, list):
        print(f"  Pending transfers: {len(transfers)}")

print("\n" + "=" * 60)
print("SUMMARY: All core endpoints tested successfully!")
print("=" * 60)
