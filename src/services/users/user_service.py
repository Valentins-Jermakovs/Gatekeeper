# =====================================================
#                       imports
# =====================================================
# Libraries:
from fastapi import HTTPException
from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession
# Schemas:
from schemas import (
    UserResponse, 
    UserEmailRequest, 
    UserPasswordChangeRequest, 
    UserUsernameChangeRequest,
    SetPasswordRequest,
    ChangeUsersRolesRequest,
    ChangeUsersRolesResponse,
    RemoveUsersRolesResponse,
    ChangeUserStatusRequest,
    ChangeUserStatusResponse
)
# Models:
from models import User, Role, UserRoles
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


# ========== Users administration endpoints ==========

# Function for changing users roles
async def add_users_roles(
    data: ChangeUsersRolesRequest,
    current_user_roles: list[str],
    current_user_id: int,
    db: AsyncSession
) -> ChangeUsersRolesResponse:

    # Check if user has admin role
    if "admin" not in current_user_roles:
        raise HTTPException(403, "Forbidden")
    
    # Check if admin is trying to modify own roles
    if current_user_id in data.users:
        raise HTTPException(
        status_code=400,
        detail="Admin cannot modify own roles"
    )

    # Get role
    role = (await db.exec(
        select(Role).where(Role.name == data.role)
    )).first()

    if not role:
        raise HTTPException(404, "Role not found")

    # Get all users at once
    users = (await db.exec(
        select(User).where(User.id.in_(data.users))
    )).all()

    # Check if all users exist
    found_user_ids = {u.id for u in users}
    missing_users = set(data.users) - found_user_ids

    # get existing relations in one query
    existing_roles = await db.exec(
        select(UserRoles).where(
            UserRoles.user_id.in_(found_user_ids),
            UserRoles.role_id == role.id
        )
    )

    # Create set of existing relations
    existing_set = {
        (r.user_id, r.role_id)
        for r in existing_roles.all()
    }

    # Add new relations
    for user in users:
        if (user.id, role.id) in existing_set:
            continue

        db.add(UserRoles(
            user_id=user.id,
            role_id=role.id
        ))

    await db.commit()

    return ChangeUsersRolesResponse(
        added_to=list(found_user_ids),
        skipped_existing=len(existing_set),
        missing_users=list(missing_users)
    )
        

async def remove_users_roles(
    data: ChangeUsersRolesRequest,
    current_user_roles: list[str],
    current_user_id: int,
    db: AsyncSession
) -> RemoveUsersRolesResponse:

    # Check if user has admin role
    if "admin" not in current_user_roles:
        raise HTTPException(403, "Forbidden")
    
    # Check if admin is trying to modify own roles
    if current_user_id in data.users:
        raise HTTPException(
        status_code=400,
        detail="Admin cannot modify own roles"
    )

    # Get role
    role = (await db.exec(
        select(Role).where(Role.name == data.role)
    )).first()

    if not role:
        raise HTTPException(404, "Role not found")

    # Get all users at once
    users = (await db.exec(
        select(User).where(User.id.in_(data.users))
    )).all()

    # Check if all users exist
    found_user_ids = {u.id for u in users}
    missing_users = set(data.users) - found_user_ids

    # get existing relations
    existing_roles = await db.exec(
        select(UserRoles).where(
            UserRoles.user_id.in_(found_user_ids),
            UserRoles.role_id == role.id
        )
    )

    # Create set of existing relations
    existing_map = {
        r.user_id for r in existing_roles.all()
    }


    removed_from = []
    skipped_not_existing = []

    # Remove relations
    for user_id in found_user_ids:

        if user_id not in existing_map:
            skipped_not_existing.append(user_id)
            continue

        await db.exec(
            delete(UserRoles).where(
                UserRoles.user_id == user_id,
                UserRoles.role_id == role.id
            )
        )

        removed_from.append(user_id)

    await db.commit()

    return RemoveUsersRolesResponse(
        removed_from=removed_from,
        skipped_not_existing=skipped_not_existing,
        missing_users=list(missing_users)
    )


# Change user status
async def change_user_status(
    data: ChangeUserStatusRequest,
    current_user_roles: list[str],
    current_user_id: int,
    db: AsyncSession
) -> ChangeUserStatusResponse:

    if "admin" not in current_user_roles:
        raise HTTPException(403, "Forbidden")

    # Check if admin is trying to modify own roles
    if current_user_id in data.users:
        raise HTTPException(
        status_code=400,
        detail="Admin cannot modify own roles"
    )

    target_ids = set(data.users)

    users = (await db.exec(
        select(User).where(User.id.in_(target_ids))
    )).all()

    if not users:
        raise HTTPException(404, "No users found")

    found_user_ids = {u.id for u in users}
    missing_users = target_ids - found_user_ids

    for user in users:
        if user.active != data.active:
            user.active = data.active

    await db.commit()

    return ChangeUserStatusResponse(
        changed=list(found_user_ids),
        skipped_not_existing=list(missing_users),
        missing_users=list(missing_users)
    )