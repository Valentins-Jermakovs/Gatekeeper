# Bibliotēku, servisu, modeļu, shēmu imports
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from src.models import User, Role, UserRoles
from src.schemas.registration import Registration as RegistrationSchema
from src.schemas.token import Token as TokenSchema
from src.services.passwords.hash_password import hash_password
from src.services.tokens.access.create_access_token import create_access_token
from src.services.tokens.refresh.refresh_token import (
    create_refresh_token,
    save_refresh_token
)


# Lietotāja reģistrācijas metode
async def registration(
    db: AsyncSession, 
    user_registration_data: RegistrationSchema
) -> TokenSchema:
    # ===== Lietotāja eksistences pārbaude =====

    # Normalizējam lietotāja datus
    user_registration_data.username = user_registration_data.username.lower()
    user_registration_data.email = user_registration_data.email.lower()

    # Pārbaude uz lietotāja eksistenci DB
    result = await db.exec(
        select(User).where(User.username == user_registration_data.username)
    )
    
    existing_user = result.first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    

    # Pārbaude uz e-pastu DB
    result = await db.exec( 
        select(User).where(User.email == user_registration_data.email)
    )

    existing_email = result.first()

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    

    # ===== Jaunā lietotāja reģistrācija =====
    
    new_user = User(
        username=user_registration_data.username,
        email=user_registration_data.email,
        password_hash=await hash_password(user_registration_data.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # ===== Jaunā lietotāja 'user' lomas piešķiršana =====

    result = await db.exec(
        select(Role).where(Role.name == "user")
    )

    role = result.first()

    if role:
        db.add(
            UserRoles(
                user_id=new_user.id, 
                role_id=role.id
            )
        )
        await db.commit()

    
    # ===== Tokenu izveide =====

    access_token = await create_access_token(user_id=new_user.id, roles=["user"])
    refresh_token = await create_refresh_token()
    await save_refresh_token(refresh_token, new_user.id, db)

    return TokenSchema(
        access_token=access_token,
        refresh_token=refresh_token
    )