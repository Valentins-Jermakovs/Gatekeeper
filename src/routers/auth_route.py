# Bibliotēku, shēmu, servisu imports
from fastapi import APIRouter, Depends
from src.schemas.token import Token as TokenSchema
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
from src.config.db_dependency import get_db
from src.schemas.login import Login as LoginSchema
from src.services.login import login as login_user
from src.schemas.registration import Registration as RegistrationSchema
from src.services.registration import registration as register_user
from src.services.logout import logout

# Router objekta izveide
router = APIRouter(
    prefix="/auth",
)

# Lietotāja login endpoints
@router.post(
    "/login",
    response_model=TokenSchema,
    summary="Authenticate a user",
)
async def user_login_endpoint(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    data = LoginSchema(
        username=form_data.username,
        password=form_data.password
    )

    return await login_user(db=db, data=data)


# Lietotāja reģistrācijas endpoints
@router.post(
    "/register",
    summary="Create a new user",
    response_model=TokenSchema
)
async def user_registration_endpoint(
    data: RegistrationSchema,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    return await register_user(data=data, db=db)


# Logout enpoints
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
    return await logout(db=db, refresh_token=refresh_token)