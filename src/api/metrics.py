import psutil
from fastapi import APIRouter

# Router object
router = APIRouter(
    prefix="/metrics",
    tags=["Metrics services"],
)

@router.get("/stats")
async def metrics():
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_used_mb":
            round(psutil.virtual_memory().used / 1024 / 1024),
    }