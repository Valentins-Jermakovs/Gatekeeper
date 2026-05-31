# Importē nepieciešamas bibliotēkas
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime, timezone

# Lietotāja modelis
class User(SQLModel, table=True):

    # Tabulas nosaukums
    __tablename__ = "users"

    # Lietotāja identifikators
    id: int | None = Field(default=None, primary_key=True)
    
    username: Optional[str] = Field(        # Lietotājvārds
        default=None, 
        max_length=50, 
        index=True, 
        unique=True
    )  

    password_hash: Optional[str] = Field(   # Šifrēta parole
        default=None,
        max_length=255
    )  

    email: str = Field(                     # E-pasts
        max_length=100, 
        index=True, 
        unique=True
    )  

    auth_provider: str = Field(             # Auth provider
        default="local", 
        max_length=20
    )  

    created_at: datetime = Field(           # Reģistrācijas laiks
        default_factory=lambda: datetime.now(timezone.utc)
    )  

    active: bool = Field(                   # Lietotāja statuss
        default=True
    )  