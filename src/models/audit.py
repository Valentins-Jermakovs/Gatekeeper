from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(index=True)
    
    action: str = Field(index=True)  # e.g. "user.change_email"
    
    entity_type: str = Field(index=True)  # "user", "role"
    entity_id: Optional[int] = Field(default=None, index=True)

    success: bool = Field(default=True)

    meta: dict[str, Any] = Field(
        sa_column=Column(JSONB),
        default_factory=dict
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(), index=True)