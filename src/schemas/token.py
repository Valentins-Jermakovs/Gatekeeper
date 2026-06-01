# =====================================================
#                       imports
# =====================================================
from pydantic import BaseModel
# =====================================================

# =====================================================
#                       Shēmas
# =====================================================

# Shēma tokenam - atbilde
class TokenResponse(BaseModel):

    access_token: str
    token_type: str = "bearer"
    refresh_token: str

# Shēma tokenam - vaicājums
class TokenRequest(BaseModel):

    access_token: str
    token_type: str = "bearer"
    refresh_token: str

# Shēma tokenam - pārbaude
class TokenCheckRequest(BaseModel):

    access_token: str
    token_type: str = "bearer"

# Shēma tokenam - pārbaudes atbilde
class TokenCheckResponse(BaseModel):

    access_token: str
    token_type: str = "bearer"