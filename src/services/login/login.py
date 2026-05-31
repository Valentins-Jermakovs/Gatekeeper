# Bibliotēku, modeļu, shēmu, servisu imports
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from schemas.login import LoginSchema
from schemas.token import TokenSchema
from services.passwords.verify_password import verify_password
from services.tokens.refresh.refresh_token import (
    delete_refresh_token_by_user_id,
    create_refresh_token,
    save_refresh_token
)
from services.tokens.access.create_access_token import create_access_token
from models import UserModel, RoleModel, UserRolesModel


# Metode priekš login
async def login(
    db: AsyncSession,
    data: LoginSchema
) -> TokenSchema:
    
    # Normalizē lietotājvārdu
    username = data.username.lower()

    # Meklē lietotāju
    result = await db.exec(
        select(UserModel).where(UserModel.username == username)
    )

    user = result.first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Paroles pārbaude
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Pārbauda, vai lietotājs nav bloķēts
    if not user.active:
        raise HTTPException(status_code=403, detail="User is blocked")
    
    # ===== Tokenu rotācija (refresh) =====

    # Dzēš veco refresh tokenu
    await delete_refresh_token_by_user_id(user_id=user.id, db=db)

    # Jaunā tokena izveide
    new_refresh_token = await create_refresh_token()
    await save_refresh_token(refresh_token=new_refresh_token, user_id=user.id, db=db)

    # ===== Access tokena izveide =====

    # Lietotāja lomu ieguve
    result = await db.exec(
        select(RoleModel.name)
        .join(UserRolesModel, UserRolesModel.role_id == RoleModel.id)
        .where(UserRolesModel.user_id == user.id)
    )

    roles = result.all()

    access_token = await create_access_token(user_id=user.id, roles=roles)

    return TokenSchema(
        access_token=access_token,
        refresh_token=new_refresh_token
    )