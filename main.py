from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (
    auth_router,
    concert_router,
    ticket_router,
    scan_router,
    transfer_router
)

# Simple startup event to ensure db is initialized
startup_done = False

app = FastAPI(
    title="Concert Ticket QR System",
    description="API for managing concert tickets with QR codes, authentication, and attendance tracking",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_router)
app.include_router(concert_router)
app.include_router(ticket_router)
app.include_router(scan_router)
app.include_router(transfer_router)


@app.get("/")
def read_root():
    """Root endpoint."""
    print("DEBUG: Root endpoint called")
    return {
        "message": "Concert Ticket QR System API v2.0",
        "docs": "/docs",
        "health": "ok",
        "features": [
            "User authentication",
            "Concert management",
            "Ticket QR generation",
            "Sales & attendance tracking",
            "Ticket transfers"
        ]
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    print("DEBUG: Health endpoint called")
    return {"status": "healthy"}

