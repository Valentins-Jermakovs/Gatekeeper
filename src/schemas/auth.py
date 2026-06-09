# =====================================================
#                       imports
# =====================================================
from pydantic import BaseModel, Field, EmailStr
# =====================================================


# Login schema for authentication
class LoginRequest(BaseModel):

    # Username
    username: str = Field(min_length=1, max_length=50)
    # Password
    password: str = Field(min_length=8, max_length=255)

# Registration schema
class RegistrationRequest(BaseModel):

    # Username
    username: str = Field(min_length=1, max_length=50)
    # Email
    email: EmailStr = Field(max_length=255)
    # Password
    password: str = Field(min_length=8, max_length=255)