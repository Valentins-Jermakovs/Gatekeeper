# =========================================================================
#                                imports
# =========================================================================
# Libraries:
from fastapi import Request
from authlib.integrations.starlette_client import OAuth
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
# Schemas:
from schemas import (
    LoginRequest, 
    RegistrationRequest,
    TokenResponse, 
)
# Services:
import services.password.password_service as password_service
import services.tokens.token_service as token_service
# Models:
from models import User, Role, UserRoles, RefreshToken
# =========================================================================


# =========================================================================
#                             Business logic
# =========================================================================

# ================= Registration ========================
async def register_user(
    db: AsyncSession, 
    user_registration_data: RegistrationRequest
) -> TokenResponse:
    
    # Check user existence

    # Normalize username and email
    user_registration_data.username = user_registration_data.username.lower()
    user_registration_data.email = user_registration_data.email.lower()

    # Check if user already exists
    result = await db.exec(
        select(User).where(User.username == user_registration_data.username)
    )
    
    existing_user = result.first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    

    # Check if email already exists
    result = await db.exec( 
        select(User).where(User.email == user_registration_data.email)
    )

    existing_email = result.first()

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    

    # New user registration
    
    new_user = User(
        username=user_registration_data.username,
        email=user_registration_data.email,
        password_hash=await password_service.hash_password(user_registration_data.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Append user role (user) to database

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

    
    # Token generation

    access_token = await token_service.create_access_token(
        user_id=new_user.id, 
        roles=["user"]
    )

    refresh_token = await token_service.create_refresh_token()
    await token_service.save_refresh_token(refresh_token, new_user.id, db)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


# ========================= Login ================================
async def authenticate_user(
    db: AsyncSession,
    data: LoginRequest
) -> TokenResponse:
    
    # Normalize username
    username = data.username.lower()

    # Search for user
    result = await db.exec(
        select(User).where(User.username == username)
    )

    user = result.first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check password
    if not password_service.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check user status
    if not user.active:
        raise HTTPException(status_code=403, detail="User is blocked")
    
    # Token rotation

    # Remove old refresh token
    await token_service.delete_refresh_token_by_user_id(user_id=user.id, db=db)

    # Create new refresh token
    new_refresh_token = await token_service.create_refresh_token()
    await token_service.save_refresh_token(
        refresh_token=new_refresh_token, 
        user_id=user.id, db=db
    )

    # Create access token

    # Get user roles
    result = await db.exec(
        select(Role.name)
        .join(UserRoles, UserRoles.role_id == Role.id)
        .where(UserRoles.user_id == user.id)
    )

    roles = result.all()

    access_token = await token_service.create_access_token(user_id=user.id, roles=roles)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


# ========================= Logout =================================
async def logout_user(
    db: AsyncSession,
    refresh_token: str,
) -> dict:
    
    # Remove refresh token
    await token_service.delete_refresh_token(
        refresh_token=refresh_token, 
        db=db
    )

    return {
        "msg": "Logout successful"
    }