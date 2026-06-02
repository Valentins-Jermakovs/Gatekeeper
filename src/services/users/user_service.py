# =====================================================
#                       imports
# =====================================================
# Libraries:
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
# Schemas:
from schemas import (
    UserResponse, 
    UserEmailRequest, 
    UserPasswordChangeRequest, 
    UserUsernameChangeRequest,
    SetPasswordRequest
)
# Models:
from models import User
# Services:
import services.password.password_service as password_service
from dotenv import load_dotenv
import os
# =====================================================


# =====================================================
#                   Business logic
# =====================================================

# Function for getting user info
async def get_user_info(
    user_id: int,
    user_roles: list,
    db: AsyncSession
) -> UserResponse:
    
    # Get current user from DB

    result = await db.exec(
        select(User).where(User.id == user_id)
    )

    user = result.first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Create user response
    user = UserResponse(
        username=user.username,
        email=user.email,
        roles=user_roles,
        created_at=user.created_at,
        active=user.active
    )

    return user

# ============ User self modification endpoints ============

# Function for changing user email
async def change_user_email(
    user_id: int,
    user_roles: list[str],
    data: UserEmailRequest,
    db: AsyncSession
) -> UserResponse:
    
    # Normalize email
    data.email = data.email.lower()

    # Get current user from DB
    result = await db.exec(
        select(User).where(User.id == user_id)
    )

    user = result.first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Try to find user with new email
    result = await db.exec(
        select(User).where(User.email == data.email)
    )

    existing_user = result.first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    # Update user email
    user.email = data.email

    await db.commit()
    await db.refresh(user)

    return await get_user_info(
        user_id=user_id, 
        user_roles=user_roles, 
        db=db
    )


# Function for changing username
async def change_user_username(
    user_id: int,
    user_roles: list[str],
    data: UserUsernameChangeRequest,
    db: AsyncSession
) -> UserResponse:
    
    # Get current user from DB
    result = await db.exec(
        select(User).where(User.id == user_id)
    )

    user = result.first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Check username uniqueness
    result = await db.exec(
        select(User).where(User.username == data.new_username)
    )

    existing_user = result.first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this username already exists"
        )
    
    # Update user username
    user.username = data.new_username

    await db.commit()
    await db.refresh(user)

    return await get_user_info(
        user_id=user_id, 
        user_roles=user_roles, 
        db=db
    )


# Function for changing user password
async def change_user_password(
    user_id: int,
    user_roles: list[str],
    data: UserPasswordChangeRequest,
    db: AsyncSession
) -> UserResponse:
    
    # Get current user from DB
    result = await db.exec(
        select(User).where(User.id == user_id)
    )

    user = result.first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    if user.password_hash is None:
        raise HTTPException(
            status_code=400,
            detail="Password is not set. Use set-password endpoint."
        )

    # verify current password
    if not await password_service.verify_password(
        data.old_password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid current password"
        )

    # update password
    user.password_hash = await password_service.hash_password(data.new_password)

    await db.commit()
    await db.refresh(user)

    return await get_user_info(
        user_id=user_id,
        user_roles=user_roles,
        db=db
    )


async def set_user_password(
    user_id: int,
    user_roles: list[str],
    data: SetPasswordRequest,
    db: AsyncSession
):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.password_hash is not None:
        raise HTTPException(
            status_code=400,
            detail="Password is already set"
        )

    user.password_hash = await password_service.hash_password(data.password)

    await db.commit()

    return await get_user_info(
        user_id=user_id,
        user_roles=user_roles,
        db=db
    )