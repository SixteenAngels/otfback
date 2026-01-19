"""Seed 21 static test accounts into the database - Admin + 10 Sales + 10 Verify"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from app.models.base import Base
from app.models.user import User
from app.settings import settings
import secrets
import string

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Build accounts dynamically: 1 Admin + 10 Sales + 10 Verify
def gen_password(length: int = 6) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def build_accounts():
    accounts = []
    # Admin - can create more users
    accounts.append({"username": "otf", "email": "admin@otf.com", "password": "cows12", "role": "admin"})

    # 10 Sales Users (Stage 1: Confirm ticket sale before giving out)
    for i in range(1, 11):
        accounts.append({
            "username": f"sales{i}",
            "email": f"sales{i}@concert.com",
            "password": gen_password(6),
            "role": "scanner",
        })

    # 10 Verify Users (Stage 2: Verify ticket validity at venue)
    for i in range(1, 11):
        accounts.append({
            "username": f"verify{i}",
            "email": f"verify{i}@concert.com",
            "password": gen_password(6),
            "role": "scanner",
        })

    return accounts


accounts = build_accounts()


async def seed_accounts():
    """Create all test accounts"""
    engine = create_async_engine(settings.database_url, echo=False)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        out_lines = []
        # Check if accounts already exist
        for account in accounts:
            existing = await session.execute(
                __import__("sqlalchemy").select(User).filter_by(username=account["username"])
            )
            if existing.scalars().first():
                print(f"Skipping {account['username']} - already exists")
                out_lines.append(f"SKIP {account['username']} {account['email']} {account['role']}")
                continue

            user = User(
                username=account["username"],
                email=account["email"],
                hashed_password=pwd_context.hash(account["password"]),
                role=account["role"],
                is_active=True,
            )
            session.add(user)
            print(f"✅ Created {account['role']:8} | {account['username']:10}")
            out_lines.append(f"CREATED {account['username']} {account['email']} {account['password']} {account['role']}")

        await session.commit()

    await engine.dispose()

    # Write credentials to file and print summary
    out_path = "seeded_accounts.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Seeded accounts (username email password role)\n")
        for line in out_lines:
            f.write(line + "\n")

    print("\n" + "="*70)
    print("✅ Seed complete. Accounts created or skipped listed below")
    print("="*70)
    print(f"\nSaved credentials to: {out_path}\n")
    for line in out_lines:
        print(line)

if __name__ == "__main__":
    asyncio.run(seed_accounts())
