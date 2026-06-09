# =====================================================
#                       imports
# =====================================================
from datetime import datetime
from pydantic import BaseModel
from typing import Any
# =====================================================


# Audit log response
class AuditLogResponse(BaseModel):

    # id
    id: int

    # audit log details
    user_id: int
    action: str
    entity_type: str
    entity_id: int | None
    success: bool
    meta: dict[str, Any]
    created_at: datetime


# Audit logs response
class AuditLogsResponse(BaseModel):
    logs: list[AuditLogResponse]