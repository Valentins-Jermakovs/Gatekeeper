# =====================================================
#                       imports
# =====================================================
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
# =====================================================

# User model
class User(SQLModel, table=True):

    # Table name
    __tablename__ = "users"

    # User id
    id: int | None = Field(default=None, primary_key=True)
    
    username: Optional[str] = Field(        # Username
        default=None, 
        max_length=50, 
        index=True, 
        unique=True
    )  

    password_hash: Optional[str] = Field(   # User password
        default=None,
        max_length=255
    )  

    email: str = Field(                     # Email
        max_length=100, 
        index=True, 
        unique=True
    )

    auth_provider: str = Field(             # Auth provider
        default="local", 
        max_length=20
    )  

    created_at: datetime = Field(           # Registration date
        default_factory=lambda: datetime.now()
    )  

    active: bool = Field(                   # User status
        default=True
    )  