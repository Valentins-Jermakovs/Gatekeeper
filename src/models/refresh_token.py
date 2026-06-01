# =====================================================
#                   imports
# =====================================================
from sqlmodel import Field, SQLModel
from datetime import datetime, timedelta
# =====================================================

# Refresh token model
class RefreshToken(SQLModel, table=True):

    # Table name
    __tablename__ = "refresh_tokens"

    # Primary id
    id: int | None = Field(default=None, primary_key=True)

    # Foreign key to user id
    user_id: int = Field(foreign_key="users.id")

    # Refresh token
    refresh_token: str = Field(max_length=256, unique=True, index=True)
    
    # =================================================
    #                   Time data fields
    # ================================================

    # Token registration time and date
    created_at: datetime = Field(
        default_factory=lambda: datetime.now()
    )
    # Token expiration date
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(days=7)
    )


