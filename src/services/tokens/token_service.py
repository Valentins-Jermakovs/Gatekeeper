# =====================================================
#                       imports
# =====================================================
# Bibliotēkas:
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import secrets
import os
# Shēmas:
from schemas import TokenResponse
# Modeļi:
from models import RefreshToken, User, UserRoles, Role
# =====================================================


# =======================================
#               .env
# =======================================

# Nolasa .env faila saturu
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY nav iestatīts .env failā")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "20"))
except ValueError:
    ACCESS_TOKEN_EXPIRE_MINUTES = 20

# =======================================


# =======================================================
#                   Biznesa loģika
# =======================================================
# =======================================================
#                   Access tokens
# =======================================================

# Metode access tokena veidošanai
async def create_access_token(
    user_id: int,
    roles: list[str]
) -> str:

    # Kodē tokenā:
    #   * lietotāja identifikatoru
    #   * lomas
    to_encode = {
        "sub": str(user_id),
        "roles": roles
    }

    # Aprēķina, kad tokens beigsies
    expire = datetime.now() + (
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Tokena papildināšana - laiki
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now().timestamp())
    })

    # Atgriež tokenu
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Tokenu atjaunošanas mehānisms
async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession
) -> TokenResponse:

    # ===== Refresh tokens =====

    # Iegūst esošo tokenu
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

    # Tokena pārbaude
    # Ja beidzas termiņš
    if token.expires_at < datetime.now():
        await db.delete(token)
        await db.commit()

        raise HTTPException(
            status_code=401,
            detail="Refresh token expired"
        )

    # Pārbauda lietotāju
    user_result = await db.exec(
        select(User).where(User.id == token.user_id)
    )

    user = user_result.first()

    if not user or not user.active:
        raise HTTPException(
            status_code=401,
            detail="User inactive"
        )

    # Tokenu rotācija
    await db.delete(token)
    await db.commit()

    # Jauno tokenu izveide
    new_refresh_token = await create_refresh_token()
    await save_refresh_token(new_refresh_token, token.user_id, db)

    # ===== Access tokena izveide =====

    # Lietotāja lomu ieguve
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


# Metode access tokena validācijai
async def verify_access_token(token: str) -> dict:
    try:
        # Pārbauda, vai token ir derīgs
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM]
        )

        return payload
    
    # Kļūdu apstrāde
    # Ja tokens nav derīgs
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token has expired")
    
    # Ja tokena signatūra nav derīga
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    
# =======================================================
#                   Refresh tokens
# =======================================================

# Metode izveido refresh tokenu
async def create_refresh_token() -> str:
    return secrets.token_urlsafe(32)


# Metode refresh tokena saglabāšanai
async def save_refresh_token(
    refresh_token: str,
    user_id: int,
    db: AsyncSession,
) -> RefreshToken:

    # Tokena izveide
    token = RefreshToken(
        user_id=user_id,
        refresh_token=refresh_token,
    )

    # Darbs ar DB
    db.add(token)

    await db.commit()
    await db.refresh(token)

    # Atgriež tokenu
    return token


# Metode, lai izdzēst refresh tokenu - pēc tokena
async def delete_refresh_token(
    refresh_token: str,
    db: AsyncSession
) -> None:

    result = await db.exec(
        select(RefreshToken).where(
            RefreshToken.refresh_token == refresh_token
        )
    )

    # Pārbaude, vai tokenu ir izveidots
    token_obj = result.first()

    # Dzēšana
    if token_obj:
        await db.delete(token_obj)
        await db.commit()


# Metode, lai izdzēst refresh tokenu, pēc lietotāja id
async def delete_refresh_token_by_user_id(
    user_id: int,
    db: AsyncSession
) -> None:
    
    result = await db.exec(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id
        )
    )

    # Pārbaude, vai tokenu ir izveidots
    token_obj = result.first()

    # Dzēšana
    if token_obj:
        await db.delete(token_obj)
        await db.commit()