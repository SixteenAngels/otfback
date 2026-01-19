#!/usr/bin/env python
"""
Quick demo script: Verify QR code pipeline works end-to-end.
"""
from fastapi.testclient import TestClient
from main import app
import base64
from PIL import Image
from io import BytesIO

client = TestClient(app)

print("\n" + "="*70)
print("  QR CODE INTEGRATION - VERIFICATION DEMO")
print("="*70)

# Test 1: Dev random QR generator
print("\n[1] Testing dev random QR generator endpoint...")
resp = client.get('/api/tickets/dev/random-qr?size=29&module_size=10')
if resp.status_code == 200:
    print(f"    ✓ Status: {resp.status_code}")
    print(f"    ✓ Content-Type: {resp.headers.get('content-type')}")
    print(f"    ✓ PNG Size: {len(resp.content)} bytes")
    
    # Verify it's valid PNG
    try:
        img = Image.open(BytesIO(resp.content))
        print(f"    ✓ Valid PNG image: {img.size[0]}x{img.size[1]} pixels")
    except Exception as e:
        print(f"    ✗ Invalid PNG: {e}")
else:
    print(f"    ✗ Status: {resp.status_code}")

# Test 2: Check API health
print("\n[2] Testing API health...")
resp = client.get('/health')
if resp.status_code == 200:
    print(f"    ✓ Health check: {resp.json()['status']}")
else:
    print(f"    ✗ Health check failed: {resp.status_code}")

# Test 3: Generate multiple QRs to ensure uniqueness
print("\n[3] Testing QR code uniqueness (generating 3 samples)...")
qr_hashes = []
for i in range(3):
    resp = client.get('/api/tickets/dev/random-qr')
    if resp.status_code == 200:
        qr_hashes.append(hash(resp.content))
        print(f"    ✓ QR {i+1}: {len(resp.content)} bytes")

if len(set(qr_hashes)) == 3:
    print(f"    ✓ All QR codes are unique")
else:
    print(f"    ⚠ Some QR codes may be identical")

# Test 4: Custom parameters
print("\n[4] Testing custom QR parameters...")
test_params = [
    {"size": 21, "module_size": 8, "border": 2},
    {"size": 29, "module_size": 12, "border": 4},
    {"size": 33, "module_size": 6, "border": 3},
]

for params in test_params:
    qs = "&".join([f"{k}={v}" for k, v in params.items()])
    resp = client.get(f'/api/tickets/dev/random-qr?{qs}')
    if resp.status_code == 200:
        img = Image.open(BytesIO(resp.content))
        print(f"    ✓ Params {params}: {img.size[0]}x{img.size[1]} px, {len(resp.content)} bytes")

print("\n" + "="*70)
print("  FRONTEND INTEGRATION NOTES:")
print("="*70)
print("""
Changes made to AdminDashboard.jsx:
  ✓ Added 'useDevQR' state toggle
  ✓ Added toggle button "🎲 Dev QR ON/OFF"
  ✓ When enabled: displays random QR from /api/tickets/dev/random-qr
  ✓ When disabled: displays stored base64 QR codes
  ✓ Download button is hidden when Dev QR is enabled
  
Backend changes:
  ✓ Created app/utils/random_qr.py with QR generator
  ✓ Added /api/tickets/dev/random-qr endpoint
  ✓ Modified ticket creation to store qr_base64 (not JSON payload)
  
To test in browser:
  1. Start backend: python -m uvicorn main:app --host 127.0.0.1 --port 8000
  2. Start frontend: npm start
  3. Login as admin, select/create a concert
  4. Click "Use Dev QR" button to toggle between real and dev QR codes
  5. Generated QR codes will display with orange border when using Dev QR
""")
print("="*70 + "\n")
