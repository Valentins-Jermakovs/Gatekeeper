from datetime import datetime
from pydantic import BaseModel
from typing import Any


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: int | None
    success: bool
    meta: dict[str, Any]
    created_at: datetime


class AuditLogsResponse(BaseModel):
    logs: list[AuditLogResponse]