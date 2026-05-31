# Importē nepieciešamas bibliotēkas
from sqlmodel import Field, SQLModel
from datetime import datetime, timedelta, timezone

# Refresh tokena modelis
class RefreshToken(SQLModel, table=True):

    # Tabulas nosaukums
    __tablename__ = "refresh_tokens"

    # Unikāls id
    id: int | None = Field(default=None, primary_key=True)

    # Atsauce uz lietotāju
    user_id: int = Field(foreign_key="users.id")

    # Refresh token
    refresh_token: str = Field(max_length=256, unique=True, index=True)
    
    # Laika iestatījumi
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=7)
    )


