from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
resp = client.get('/')
print('STATUS', resp.status_code)
print(resp.json())
