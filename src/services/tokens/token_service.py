# =====================================================
#                       imports
# =====================================================
# Libraries:
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import secrets
import os
# Schemas:
from schemas import TokenResponse
# Models:
from models import RefreshToken, User, UserRoles, Role
# =====================================================


# =======================================
#               .env
# =======================================

# Read .env file
load_dotenv()

# Save .env variables
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required for token service")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "20"))
except ValueError:
    ACCESS_TOKEN_EXPIRE_MINUTES = 20
# =======================================


# =======================================================
#                   Business logic
# =======================================================
# =======================================================
#                   Access token
# =======================================================

# Function for creating access token
async def create_access_token(
    user_id: int,
    roles: list[str]
) -> str:

    # Write info to token:
    #   * user_id
    #   * roles
    to_encode = {
        "sub": str(user_id),
        "roles": roles
    }

    # Compute token expiration
    expire = datetime.now() + (
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Add token expiration
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now().timestamp())
    })

    # Encode token
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Function for refreshing access token
async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession
) -> TokenResponse:

    # Get existing refresh token
    result = await db.exec(
        select(RefreshToken).where(
            RefreshToken.refresh_token == refresh_token
        )
    )

    token = result.first()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    # Token signature check
    # If token has expired
    if token.expires_at < datetime.now():
        await db.delete(token)
        await db.commit()

        raise HTTPException(
            status_code=401,
            detail="Refresh token expired"
        )

    # User check
    user_result = await db.exec(
        select(User).where(User.id == token.user_id)
    )

    user = user_result.first()

    if not user or not user.active:
        raise HTTPException(
            status_code=401,
            detail="User inactive"
        )

    # Token delete
    await db.delete(token)
    await db.commit()

    # Create new refresh token
    new_refresh_token = await create_refresh_token()
    await save_refresh_token(new_refresh_token, token.user_id, db)

    # Access token create

    # Get user roles
    result = await db.exec(
        select(Role.name)
        .join(UserRoles, UserRoles.role_id == Role.id)
        .where(UserRoles.user_id == user.id)
    )

    roles = result.all()

    access_token = await create_access_token(user_id=user.id, roles=roles)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


# =======================================================
#                   Refresh tokens
# =======================================================

# Function for creating refresh token
async def create_refresh_token() -> str:
    return secrets.token_urlsafe(32)


# Function for saving refresh token
async def save_refresh_token(
    refresh_token: str,
    user_id: int,
    db: AsyncSession,
) -> RefreshToken:

    # Token object
    token = RefreshToken(
        user_id=user_id,
        refresh_token=refresh_token,
    )

    # Save token
    db.add(token)

    await db.commit()
    await db.refresh(token)

    return token


# Function for deleting refresh token
async def delete_refresh_token(
    refresh_token: str,
    db: AsyncSession
) -> None:

    result = await db.exec(
        select(RefreshToken).where(
            RefreshToken.refresh_token == refresh_token
        )
    )

    # Check if token exists
    token_obj = result.first()

    # Delete
    if token_obj:
        await db.delete(token_obj)
        await db.commit()


# Function for deleting refresh token by user id
async def delete_refresh_token_by_user_id(
    user_id: int,
    db: AsyncSession
) -> None:
    
    result = await db.exec(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id
        )
    )

    # Check if token exists
    token_obj = result.first()

    # Delete
    if token_obj:
        await db.delete(token_obj)
        await db.commit()