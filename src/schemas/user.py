# =====================================================
#                       imports
# =====================================================
from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import EmailStr
# =====================================================


# UserResponse Schema
class UserResponse(SQLModel):
    username: str | None
    email: str
    roles: list[str]
    created_at: datetime
    active: bool

# User Email Request Schema
class UserEmailRequest(SQLModel):
    email: EmailStr

# User password change request schema
class UserPasswordChangeRequest(SQLModel):
    old_password: str = Field(min_length=8, max_length=255)
    new_password: str = Field(min_length=8, max_length=255)

# User password set request schema
class SetPasswordRequest(SQLModel):
    password: str = Field(min_length=8, max_length=255)

# User username change request schema
class UserUsernameChangeRequest(SQLModel):
    new_username: str = Field(min_length=1, max_length=50)