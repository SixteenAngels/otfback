import sqlite3
from passlib.context import CryptContext

conn = sqlite3.connect('test_concert.db')
c = conn.cursor()
c.execute('SELECT username, hashed_password FROM users WHERE username=?', ('otf',))
row = c.fetchone()
if row:
    print(f"DB User: {row[0]}")
    print(f"DB Hash: {row[1][:50]}...")
    
    # Test verification
    pwd_context = CryptContext(schemes=['argon2', 'bcrypt'], deprecated='auto')
    try:
        is_valid = pwd_context.verify('cows12', row[1])
        print(f'Password "cows12" valid: {is_valid}')
    except Exception as e:
        print(f'Verification error: {e}')
else:
    print('User not found')
conn.close()
