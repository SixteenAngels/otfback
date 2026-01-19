# Concert Ticket QR Code System - Backend

A FastAPI-based backend for managing concert tickets with QR codes, user authentication, sales tracking, attendance verification, refunds, and ticket transfers.

## Features

- **User Authentication**: Role-based access control (Admin, Scanner, Viewer)
- **Concert Management**: Create and manage concert events
- **Ticket Generation**: Generate unique tickets with QR codes
- **Sales Tracking**: Track sold tickets with buyer information
- **Attendance Tracking**: Scan QR codes for entry and attendance
- **Refund Management**: Request and approve ticket refunds
- **Ticket Transfers**: Transfer tickets between users with approval
- **Attendance Reports**: Generate attendance statistics per concert
- **Async/Await**: Built on async SQLAlchemy with asyncpg for neon.tech
- **Database Migrations**: Alembic for version control

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with asyncpg
- **ORM**: SQLAlchemy 2.0 (async)
- **Auth**: JWT with python-jose & bcrypt
- **QR Codes**: python-qrcode
- **Server**: Uvicorn
- **Migrations**: Alembic

## Project Structure

```
backend/
├── app/
│   ├── models/              # Database models
│   │   ├── concert.py       # Concert model
│   │   ├── ticket.py        # Ticket model with refund/transfer
│   │   ├── scan.py          # Scan tracking
│   │   ├── user.py          # User & roles
│   │   ├── refund.py        # Refund requests
│   │   └── transfer.py      # Ticket transfers
│   ├── routes/              # API endpoints
│   │   ├── auth.py          # Authentication
│   │   ├── concerts.py      # Concert endpoints
│   │   ├── tickets.py       # Ticket endpoints
│   │   ├── scans.py         # Scan endpoints
│   │   ├── refunds.py       # Refund endpoints
│   │   └── transfers.py     # Transfer endpoints
│   ├── schemas/             # Pydantic schemas
│   ├── utils/               # Utilities (QR, auth)
│   ├── database.py          # Async DB config
│   └── settings.py          # App settings
├── alembic/                 # Database migrations
├── main.py                  # FastAPI app entry
├── requirements.txt         # Dependencies
├── .env.example            # Env template
├── Dockerfile              # Docker image
└── README.md              # This file
```

## Setup

### Prerequisites
- Python 3.10+
- PostgreSQL (or Neon.tech account for serverless)

### Local Installation

1. **Clone and navigate**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Run migrations**:
```bash
alembic upgrade head
```

6. **Start the server**:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

### Using Docker

```bash
docker build -t concert-api .
docker run -p 8000:8000 -e DATABASE_URL="your_db_url" concert-api
```

## Database Configuration

### Neon.tech (PostgreSQL Serverless)

Use the provided connection string from Neon:
```
DATABASE_URL=postgresql+asyncpg://neondb_owner:password@host/neondb
```

The system uses:
- `asyncpg` driver for async operations
- `NullPool` connection pooling (suitable for serverless)

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token

### Concerts (Admin)
- `POST /api/concerts/` - Create concert
- `GET /api/concerts/` - List all concerts
- `GET /api/concerts/{id}` - Get concert details

### Tickets (Admin)
- `POST /api/tickets/create/{concert_id}` - Create ticket
- `POST /api/tickets/{id}/mark-sold` - Mark ticket as sold
- `GET /api/tickets/{id}` - Get ticket details
- `GET /api/tickets/concert/{concert_id}` - List concert tickets
- `GET /api/tickets/number/{ticket_number}` - Get ticket by QR number

### Scans (Scanner/Admin)
- `POST /api/scans/` - Record a scan
- `GET /api/scans/ticket/{ticket_id}` - Get ticket scans
- `GET /api/scans/concert/{concert_id}/attendance` - Attendance stats

### Refunds
- `POST /api/refunds/request` - Request refund
- `GET /api/refunds/` - List refunds (admin)
- `POST /api/refunds/{id}/approve` - Approve refund (admin)
- `POST /api/refunds/{id}/reject` - Reject refund (admin)

### Transfers
- `POST /api/transfers/initiate` - Initiate transfer
- `GET /api/transfers/pending` - Get pending transfers
- `POST /api/transfers/{id}/accept` - Accept transfer
- `POST /api/transfers/{id}/reject` - Reject transfer

## Data Models

### User Roles
- **admin**: Full access, manages concerts and refunds
- **scanner**: Can scan tickets
- **viewer**: Read-only access

### Ticket Status
- created, sold, scanned_entry, attended, refunded, transferred

### Scan Types
- sale_confirmation, entry_check, attendance

### Refund Status
- pending, approved, rejected, completed

### Transfer Status
- pending, accepted, rejected, completed

## Error Handling

The API returns standard HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not found
- `500` - Server error

Error responses include a `detail` field with the error message.

## Security

- JWT tokens for authentication
- Bcrypt password hashing
- Role-based access control (RBAC)
- Async operations to prevent blocking
- CORS enabled for frontend integration

## Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
ENV=development
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Development

Install dev dependencies:
```bash
pip install pytest pytest-asyncio httpx
```

Run tests:
```bash
pytest
```

## Production Deployment

1. Set strong `SECRET_KEY`
2. Use production database
3. Set `ENV=production`
4. Use environment variables for secrets
5. Enable HTTPS
6. Set appropriate CORS origins
7. Use Gunicorn or similar ASGI server:

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Support

For issues and questions, check the main README in the project root.

