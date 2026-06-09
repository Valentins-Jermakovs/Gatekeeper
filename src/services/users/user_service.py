# =====================================================
#                       imports
# =====================================================
# Libraries:
from fastapi import HTTPException
from sqlmodel import select, delete, or_, func
from sqlmodel.ext.asyncio.session import AsyncSession
# Schemas:
from schemas import (
    UserResponse, 
    UserEmailRequest, 
    UserPasswordChangeRequest, 
    UserUsernameChangeRequest,
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
# Schemas:
from schemas import UserListResponse, AuditActions
# Utils:
from utils.log_writer import log_audit
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
        id=user.id,
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
    old_email = user.email
    user.email = data.email

    await db.commit()
    await db.refresh(user)

    await log_audit(
        db,
        user_id=user_id,
        action=AuditActions.USER_CHANGE_EMAIL,
        entity_type="user",
        entity_id=user_id,
        meta={
            "old_email": old_email,
            "new_email": data.email
        }
    )

    await db.commit()

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
    old_username = user.username
    user.username = data.new_username

    await db.commit()
    await db.refresh(user)

    await log_audit(
        db,
        user_id=user_id,
        action=AuditActions.USER_CHANGE_USERNAME,
        entity_type="user",
        entity_id=user_id,
        meta={
            "old_username": old_username,
            "new_username": data.new_username
        }
    )

    await db.commit()

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

    await log_audit(
        db,
        user_id=user_id,
        action=AuditActions.USER_CHANGE_PASSWORD,
        entity_type="user",
        entity_id=user_id
    )

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

    # Check admin
    if "admin" not in current_user_roles:
        raise HTTPException(403, "Forbidden")

    if current_user_id in data.users:
        raise HTTPException(
            status_code=400,
            detail="Admin cannot modify own roles"
        )

    # deduplicate input
    unique_user_ids = set(data.users)

    # get role
    role = (await db.exec(
        select(Role).where(Role.name == data.role)
    )).first()

    if not role:
        raise HTTPException(404, "Role not found")

    # fetch users
    users = (await db.exec(
        select(User).where(User.id.in_(unique_user_ids))
    )).all()

    found_user_ids = {u.id for u in users}
    missing_users = unique_user_ids - found_user_ids

    # existing relations
    existing_roles = await db.exec(
        select(UserRoles).where(
            UserRoles.user_id.in_(found_user_ids),
            UserRoles.role_id == role.id
        )
    )

    existing_set = {(r.user_id, r.role_id) for r in existing_roles.all()}

    # APPLY CHANGES
    added = []

    for user in users:
        if (user.id, role.id) in existing_set:
            continue

        db.add(UserRoles(
            user_id=user.id,
            role_id=role.id
        ))

        added.append(user.id)

    # commit FIRST
    await db.commit()

    # audit AFTER commit
    await log_audit(
        db,
        user_id=current_user_id,
        action=AuditActions.ADMIN_ADD_ROLES,
        entity_type="role",
        entity_id=role.id,
        meta={
            "role": data.role,
            "added": added,
            "missing": list(missing_users),
            "skipped_existing": list(found_user_ids - set(added))
        }
    )

    # commit SECOND
    await db.commit()

    return ChangeUsersRolesResponse(
        added_to=added,
        skipped_existing=len(found_user_ids) - len(added),
        missing_users=list(missing_users)
    )
        

async def remove_users_roles(
    data: ChangeUsersRolesRequest,
    current_user_roles: list[str],
    current_user_id: int,
    db: AsyncSession
) -> RemoveUsersRolesResponse:

    # Check admin
    if "admin" not in current_user_roles:
        raise HTTPException(403, "Forbidden")

    if current_user_id in data.users:
        raise HTTPException(
            status_code=400,
            detail="Admin cannot modify own roles"
        )

    # deduplicate input
    unique_user_ids = set(data.users)

    # get role
    role = (await db.exec(
        select(Role).where(Role.name == data.role)
    )).first()

    if not role:
        raise HTTPException(404, "Role not found")

    # fetch users
    users = (await db.exec(
        select(User).where(User.id.in_(unique_user_ids))
    )).all()

    found_user_ids = {u.id for u in users}
    missing_users = unique_user_ids - found_user_ids

    # existing relations
    existing_roles = await db.exec(
        select(UserRoles).where(
            UserRoles.user_id.in_(found_user_ids),
            UserRoles.role_id == role.id
        )
    )

    existing_map = {r.user_id for r in existing_roles.all()}

    removed_from = []
    skipped_not_existing = []

    # batch delete instead of loop
    to_remove = []

    for user_id in found_user_ids:
        if user_id not in existing_map:
            skipped_not_existing.append(user_id)
            continue

        to_remove.append(user_id)
        removed_from.append(user_id)

    if to_remove:
        await db.exec(
            delete(UserRoles).where(
                UserRoles.user_id.in_(to_remove),
                UserRoles.role_id == role.id
            )
        )

    await db.commit()

    # audit AFTER commit (correct state)
    await log_audit(
        db,
        user_id=current_user_id,
        action=AuditActions.ADMIN_REMOVE_ROLES,
        entity_type="role",
        entity_id=role.id,
        meta={
            "role": data.role,
            "removed_from": removed_from,
            "skipped_not_existing": skipped_not_existing,
            "missing_users": list(missing_users)
        }
    )

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

    changed = []
    skipped_already = []

    for user in users:
        if user.active == data.active:
            skipped_already.append(user.id)
            continue

        user.active = data.active
        changed.append(user.id)

    await db.commit()

    await log_audit(
        db,
        user_id=current_user_id,
        action=AuditActions.ADMIN_CHANGE_STATUS,
        entity_type="user",
        entity_id=None,
        meta={
            "target_users": list(target_ids),
            "changed": changed,
            "skipped_already": skipped_already,
            "missing": list(missing_users),
            "active": data.active
        }
    )

    await db.commit()

    return ChangeUserStatusResponse(
        changed=changed,
        skipped_not_existing=skipped_already,
        missing_users=list(missing_users)
    )


# Get users
async def get_users(
    db: AsyncSession, 
    limit: int, 
    offset: int, 
    current_user_roles: list[str],
    search: str | None
) -> UserListResponse:
    
    if "admin" not in current_user_roles:
        raise HTTPException(403, "Forbidden")

    query = select(User).distinct()
    count_query = select(func.count(func.distinct(User.id)))

    if search:
        query = query.join(
            UserRoles, User.id == UserRoles.user_id, isouter=True
        ).join(
            Role, Role.id == UserRoles.role_id, isouter=True
        ).where(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                Role.name.ilike(f"%{search}%")
            )
        )
        count_query = count_query.select_from(User).join(
            UserRoles, User.id == UserRoles.user_id, isouter=True
        ).join(
            Role, Role.id == UserRoles.role_id, isouter=True
        ).where(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                Role.name.ilike(f"%{search}%")
            )
        )
    else:
        count_query = count_query.select_from(User)

    query = query.limit(limit).offset(offset)

    result = await db.exec(query)
    users = result.all()

    total_result = await db.exec(count_query)
    total = total_result.one()

    user_responses = []

    for user in users:
        roles = (await db.exec(
            select(Role.name)
            .join(UserRoles)
            .where(UserRoles.user_id == user.id)
        )).all()

        user_responses.append(
            UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                roles=roles,
                active=user.active,
                created_at=user.created_at
            )
        )

    return UserListResponse(
        users=user_responses,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit < total)
    )