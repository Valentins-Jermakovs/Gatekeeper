# Bibliotēku imports
from pydantic import BaseModel

# Shēma tokenam
class TokenSchema(BaseModel):

    access_token: str
    token_type: str = "bearer"
    refresh_token: str