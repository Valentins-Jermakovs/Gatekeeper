# Importē bibliotēkas
from pydantic import BaseModel, Field

# Login formas validācijas shēma
class Login(BaseModel):

    # Lietotājvārds
    username: str = Field(min_length=1, max_length=50)
    # Parole
    password: str = Field(min_length=8, max_length=255)