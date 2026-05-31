# Importē bibliotēkas
from pydantic import BaseModel, Field, EmailStr

# Reģistrācijas formas validācijas shēma
class RegistrationSchema(BaseModel):

    # Lietotājvārds
    username: str = Field(min_length=1, max_length=50)
    # E-pasts
    email: EmailStr = Field(max_length=255)
    # Parole
    password: str = Field(min_length=8, max_length=255)