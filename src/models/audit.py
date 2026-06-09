# =====================================================
#                       imports
# =====================================================
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
# =====================================================


# AuditLog model
class AuditLog(SQLModel, table=True):

    # Table name
    __tablename__ = "audit_logs"

    # Primary key
    id: int | None = Field(default=None, primary_key=True)

    # User
    user_id: int = Field(index=True)
    
    # Action
    action: str = Field(index=True)  # e.g. "user.change_email"
    
    # Entity
    entity_type: str = Field(index=True)  # "user", "role"
    entity_id: Optional[int] = Field(default=None, index=True)

    # Success
    success: bool = Field(default=True)

    # Meta data
    meta: dict[str, Any] = Field(
        sa_column=Column(JSONB),
        default_factory=dict
    )

    # Created at timestamp
    created_at: datetime = Field(default_factory=lambda: datetime.now(), index=True)