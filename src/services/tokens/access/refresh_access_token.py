from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from datetime import datetime
from models import UserModel, RefreshTokenModel
from services.tokens.refresh.refresh_token import create_refresh_token, save_refresh_token
from schemas.token import TokenSchema
from services.tokens.access.create_access_token import create_access_token
from models import UserRolesModel, RoleModel

# Tokenu atjaunošanas mehānisms
async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession
) -> TokenSchema:

    # ===== Refresh tokens =====

    # Iegūst esošo tokenu
    result = await db.execute(
        select(RefreshTokenModel).where(
            RefreshTokenModel.refresh_token == refresh_token
        )
    )

    token = result.scalars().first()

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
    user_result = await db.execute(
        select(UserModel).where(UserModel.id == token.user_id)
    )

    user = user_result.scalars().first()

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
    result = await db.execute(
        select(RoleModel.name)
        .join(UserRolesModel, UserRolesModel.role_id == RoleModel.id)
        .where(UserRolesModel.user_id == user.id)
    )

    roles = result.scalars().all()

    access_token = await create_access_token(user_id=user.id, roles=roles)

    return TokenSchema(
        access_token=access_token,
        refresh_token=new_refresh_token
    )