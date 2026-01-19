from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
resp = client.get('/api/tickets/dev/random-qr')
print('STATUS', resp.status_code)
if resp.status_code == 200:
    with open('dev_random_qr.png', 'wb') as f:
        f.write(resp.content)
    print('Saved dev_random_qr.png')
else:
    print(resp.text)
