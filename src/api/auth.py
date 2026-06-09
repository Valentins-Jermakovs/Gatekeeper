# =========================================================================
#                               imports
# =========================================================================
# Libraries:
from fastapi import APIRouter, Depends
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
# Dependencies:
from config.db_dependency import get_db
# Services:
import services.auth.auth_service as auth
# Schemas:
from schemas import (
    LoginRequest, 
    RegistrationRequest, 
    TokenResponse,
    LogoutRequest
)
# =========================================================================


# =========================================================================
#                                Router
# =========================================================================

# Router object
router = APIRouter(
    prefix="/auth",
    tags=["Auth services"],
)

# =========================================================================
#                               Endpoints
# =========================================================================

# ===================== User login endpoint =========================

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate a user",
)
async def user_login_endpoint(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    data = LoginRequest(
        username=form_data.username,
        password=form_data.password
    )

    return await auth.authenticate_user(db=db, data=data)


# ================ User registration endpoint ======================
@router.post(
    "/register",
    summary="Create a new user",
    response_model=TokenResponse
)
async def user_registration_endpoint(
    data: RegistrationRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    return await auth.register_user(user_registration_data=data, db=db)


# ======================== Logout endpoint ================================
@router.post(
    "/logout",
    summary="Logout a user"
)
async def logout_user_endpoint(
    data: LogoutRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):

    return await auth.logout_user(
        db=db, 
        refresh_token=data.refresh_token
    )