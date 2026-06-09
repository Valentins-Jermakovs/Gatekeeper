# =====================================================
#                       imports
# =====================================================
# Libraries:
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any
# Models:
from models import AuditLog
# =====================================================

# Function for writing audit logs
async def log_audit(
    db: AsyncSession,
    *,
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    success: bool = True,
    meta: dict[str, Any] | None = None,
):
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        success=success,
        meta=meta or {},
    )

    db.add(log)