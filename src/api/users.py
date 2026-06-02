# =========================================================================
#                               imports
# =========================================================================
# Libraries:
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
# Dependencies:
from config.security import get_current_user
from config.db_dependency import get_db
# Schemas:
from schemas import (
    UserResponse, 
    UserEmailRequest, 
    UserUsernameChangeRequest,
    UserPasswordChangeRequest,
    SetPasswordRequest,
    ChangeUsersRolesRequest,
    ChangeUsersRolesResponse,
    RemoveUsersRolesResponse
)
# Services
import services.users.user_service as user_service
# =========================================================================


# =========================================================================
#                               Router object
# =========================================================================
router = APIRouter(
    prefix="/users",
    tags=["Users services"],
)
# =========================================================================


# =========================================================================
#                           Current user endpoint
# =========================================================================
@router.get("/me", response_model=UserResponse)
async def current_user_endpoint(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    
    user_id = current_user.get("sub")
    user_id = int(user_id)
    user_roles = current_user.get("roles")

    return await user_service.get_user_info(
        user_id=user_id,
        user_roles=user_roles,
        db=db
    )
# =========================================================================


# =========================================================================
#                       User self modification endpoints
# =========================================================================

# Endpoint for changing user email
@router.patch("/me/email", response_model=UserResponse)
async def change_user_email_endpoint(
    data: UserEmailRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    
    user_id = current_user.get("sub")
    user_id = int(user_id)
    user_roles = current_user.get("roles")

    return await user_service.change_user_email(
        user_id=user_id,
        user_roles=user_roles,
        data=data,
        db=db
    )


# Endpoint for changing user username
@router.patch("/me/username", response_model=UserResponse)
async def change_user_username_endpoint(
    data: UserUsernameChangeRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    
    user_id = current_user.get("sub")
    user_id = int(user_id)
    user_roles = current_user.get("roles")

    return await user_service.change_user_username(
        user_id=user_id,
        user_roles=user_roles,
        data=data,
        db=db
    )


# Endpoint for changing user password
@router.patch("/me/password", response_model=UserResponse)
async def change_user_password_endpoint(
    data: UserPasswordChangeRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    
    user_id = current_user.get("sub")
    user_id = int(user_id)
    user_roles = current_user.get("roles")

    return await user_service.change_user_password(
        user_id=user_id,
        user_roles=user_roles,
        data=data,
        db=db
    )


# Endpoint for setting password
@router.post("/me/set-password", response_model=UserResponse)
async def set_user_password_endpoint(
    data: SetPasswordRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    
    user_id = current_user.get("sub")
    user_id = int(user_id)
    user_roles = current_user.get("roles")

    return await user_service.set_user_password(
        user_id=user_id,
        user_roles=user_roles,
        data=data,
        db=db
    )

# =========================================================================


# =========================================================================
#                       User admin modification endpoints
# =========================================================================

# Endpoint for adding users roles
@router.patch("/add-roles", response_model=ChangeUsersRolesResponse)
async def add_users_roles_endpoint(
    data: ChangeUsersRolesRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ChangeUsersRolesResponse:
    
    user_id = current_user.get("sub")
    user_id = int(user_id)
    user_roles = current_user.get("roles")

    return await user_service.add_users_roles(
        data=data,
        current_user_roles=user_roles,
        current_user_id=user_id,
        db=db
    )


# Endpoint for deleting users roles
@router.delete("/remove-roles", response_model=RemoveUsersRolesResponse)
async def remove_users_roles_endpoint(
    data: ChangeUsersRolesRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> RemoveUsersRolesResponse:
    
    user_id = current_user.get("sub")
    user_id = int(user_id)
    user_roles = current_user.get("roles")

    return await user_service.remove_users_roles(
        data=data,
        current_user_roles=user_roles,
        current_user_id=user_id,
        db=db
    )