# =========================================================================
#                               imports
# =========================================================================
# Bibliotēkas:
from fastapi import APIRouter, Depends, Request
from fastapi.security import (
    OAuth2PasswordRequestForm, 
    HTTPBearer, 
    HTTPAuthorizationCredentials
)
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
from authlib.integrations.starlette_client import OAuth
import os
from urllib.parse import urlencode
from starlette.responses import RedirectResponse
# Dependencies:
from config.db_dependency import get_db
# Servisi:
import services.auth.auth_service as auth
# Shēmas:
from schemas import (
    LoginRequest, 
    RegistrationRequest, 
    TokenResponse
)
# =========================================================================


# =========================================================================
#                                Router
# =========================================================================

# Router objekta izveide
router = APIRouter(
    prefix="/auth",
    tags=["Auth services"],
)

# =========================================================================
#                               Endpoints
# =========================================================================


# ===================== Google endpoints ==================================

# http://localhost:8000/auth/google/login

oauth = OAuth()

CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url=CONF_URL,
    client_kwargs={
        "scope": "openid email profile",
    },
)

@router.get("/google/login")
async def get_google_login(request: Request):

    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    return await oauth.google.authorize_redirect(
        request,
        redirect_uri
    )


@router.get("/google/callback")
async def google_auth_handler(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    '''
    Handle Google callback
    '''
    tokens = await auth.google_auth_callback(oauth, db, request)

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173/login"
    )

    query = urlencode({
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
    })

    return RedirectResponse(
        url=f"{frontend_url}?{query}",
        status_code=303
    )

# ===================== Lietotāja login endpoints =========================

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


# ================ Lietotāja reģistrācijas endpoints ======================
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


# ======================== Logout enpoints ================================
logout_scheme = HTTPBearer()

@router.post(
    "/logout",
    summary="Logout a user"
)
async def logout_user_endpoint(
    data: Annotated[
        HTTPAuthorizationCredentials,
        Depends(logout_scheme)
    ],
    db: Annotated[AsyncSession, Depends(get_db)]
):

    refresh_token = data.credentials
    return await auth.logout_user(db=db, refresh_token=refresh_token)