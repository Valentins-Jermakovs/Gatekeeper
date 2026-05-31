# Importē bibliotēkas
from pydantic import BaseModel

# Shēma tokenam
class TokenCheckSchema(BaseModel):
    access_token: str
    token_type: str = "Bearer"