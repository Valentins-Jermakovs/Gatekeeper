# =========================================================================
#                               imports
# =========================================================================
# Libraries:
import psutil
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
# Dependencies:
from config.security import get_current_user
from config.db_dependency import get_db
# Services:
import services.audit.audit_service as audit_service
# Schemas
from schemas import AuditLogsResponse
# =========================================================================

# =========================================================================
#                                Router
# =========================================================================

# Router object
router = APIRouter(
    prefix="/metrics",
    tags=["Metrics services"],
)

# =========================================================================
#                               Endpoints
# =========================================================================

# =============== Endpoint for getting metrics =============================
@router.get("/stats")
async def metrics(
    current_user = Depends(get_current_user),
):
    # Get current user's roles
    user_roles = current_user.get("roles")

    # Allow access only for administrators
    if "admin" not in user_roles:
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    # Return current system metrics
    return {
        # CPU usage percentage
        "cpu_percent": psutil.cpu_percent(),

        # Memory usage percentage
        "memory_percent": psutil.virtual_memory().percent,

        # Used memory in megabytes
        "memory_used_mb":
            round(psutil.virtual_memory().used / 1024 / 1024),
    }


# ============= Endpoint for getting audit logs ============================
@router.get(
    "/audit",
    response_model=AuditLogsResponse
)
async def get_audit_logs_endpoint(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get current user's roles
    user_roles = current_user.get("roles")

    # Return the latest audit log entries
    return await audit_service.get_latest_audit_logs(
        db=db,
        current_user_roles=user_roles
    )


# ============= Endpoint for downloading audit logs ========================
@router.get("/audit/download")
async def download_audit_logs_endpoint(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get current user's roles
    user_roles = current_user.get("roles")

    # Generate and return audit logs as a downloadable TXT file
    return await audit_service.download_audit_logs(
        db=db,
        current_user_roles=user_roles
    )