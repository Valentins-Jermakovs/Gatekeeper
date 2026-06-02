# =====================================================
#                       imports
# =====================================================
from sqlmodel import SQLModel
from datetime import datetime
# =====================================================


# UserResponse Schema
class UserResponse(SQLModel):
    username: str | None
    email: str
    created_at: datetime
    active: bool