# =====================================================
#                       imports
# =====================================================
from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import EmailStr
from enum import Enum
from typing import Optional
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


# Roles enum
class Roles(str, Enum):
    admin = "admin"
    manager = "manager"

# Schema for users and it's roles modifications
class ChangeUsersRolesRequest(SQLModel):
    users: list[int]
    role: Roles

# Schema for users and it's roles modifications - Response
class ChangeUsersRolesResponse(SQLModel):
    added_to: list[int]
    skipped_existing: int
    missing_users: list[int]

# Schema for users and it's roles removal
class RemoveUsersRolesResponse(SQLModel):
    removed_from: list[int]
    skipped_not_existing: list[int]
    missing_users: list[int]

# Schema for change users status
class ChangeUserStatusRequest(SQLModel):
    users: list[int]
    active: bool

# Schema for response
class ChangeUserStatusResponse(SQLModel):
    changed: list[int]
    skipped_not_existing: list[int]
    missing_users: list[int]

# Schema for user query params
class UsersQueryParams(SQLModel):
    limit: int = 20
    offset: int = 0
    search: Optional[str] = None

# Schema for user list
class UserListResponse(SQLModel):
    users: list[UserResponse]
    total: int
    limit: int
    offset: int
    has_more: bool