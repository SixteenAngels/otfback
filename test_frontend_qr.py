#!/usr/bin/env python
"""
Test script: Generate sample QR codes and verify the API endpoint works.
"""
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.ticket import Ticket, TicketStatus
from app.database import get_db
from app.utils.qr_generator import generate_qr_code
import uuid

client = TestClient(app)

print("=" * 60)
print("Testing Dev QR Endpoint")
print("=" * 60)

# Test 1: Dev random QR endpoint
print("\n1. Testing /api/tickets/dev/random-qr endpoint...")
resp = client.get('/api/tickets/dev/random-qr')
print(f"   Status: {resp.status_code}")
print(f"   Content-Type: {resp.headers.get('content-type')}")
print(f"   Size: {len(resp.content)} bytes")
if resp.status_code == 200:
    with open('test_dev_qr_1.png', 'wb') as f:
        f.write(resp.content)
    print("   ✓ Saved test_dev_qr_1.png")

# Test 2: Different parameters
print("\n2. Testing with custom parameters...")
resp = client.get('/api/tickets/dev/random-qr?size=21&module_size=8&border=2')
print(f"   Status: {resp.status_code}")
print(f"   Size: {len(resp.content)} bytes")
if resp.status_code == 200:
    with open('test_dev_qr_2.png', 'wb') as f:
        f.write(resp.content)
    print("   ✓ Saved test_dev_qr_2.png with custom params")

# Test 3: Root endpoint
print("\n3. Testing root endpoint...")
resp = client.get('/')
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"   ✓ {data['message']}")

print("\n" + "=" * 60)
print("Tests Complete!")
print("=" * 60)
