from .auth import router as auth_router
from .concerts import router as concert_router
from .tickets import router as ticket_router
from .scans import router as scan_router
from .transfers import router as transfer_router

__all__ = [
    "auth_router",
    "concert_router",
    "ticket_router",
    "scan_router",
    "transfer_router"
]
