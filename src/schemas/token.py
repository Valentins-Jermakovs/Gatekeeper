# =====================================================
#                       imports
# =====================================================
from pydantic import BaseModel
# =====================================================

# =====================================================
#                       Schemas
# =====================================================

# Token schema for response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str

# Token schema for request
class TokenRequest(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str

# Token schema for check
class TokenCheckRequest(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Token schema for response
class TokenCheckResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Token schema for request
class RefreshRequest(BaseModel):
    refresh_token: str