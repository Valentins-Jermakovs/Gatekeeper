# =====================================================
#                       imports
# =====================================================
from pydantic import BaseModel
# =====================================================


# Logout request
class LogoutRequest(BaseModel):
    refresh_token: str