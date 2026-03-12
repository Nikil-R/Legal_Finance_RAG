from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Simple health check - no dependencies."""
    return {"status": "healthy"}

@router.get("/health/ready")
async def readiness_check():
    """Readiness check - no heavy dependencies."""
    return {"status": "ready", "dependencies": "loaded"}
