"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
async def health():
    """Basic health check for orchestration / monitoring."""
    return {"status": "healthy", "service": "aegisnet"}
