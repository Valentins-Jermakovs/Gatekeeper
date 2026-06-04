# =========================================================================
#                               imports
# =========================================================================
# Libraries:
import psutil
from fastapi import APIRouter, Depends, HTTPException
# Dependencies:
from config.security import get_current_user
# =========================================================================

# Router object
router = APIRouter(
    prefix="/metrics",
    tags=["Metrics services"],
)

@router.get("/stats")
async def metrics(
    current_user = Depends(get_current_user),
):
    user_roles = current_user.get("roles")

    if "admin" not in user_roles:
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_used_mb":
            round(psutil.virtual_memory().used / 1024 / 1024),
    }