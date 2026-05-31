# Importē bibliotēkas, modeļus
import secrets
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models import RefreshToken


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