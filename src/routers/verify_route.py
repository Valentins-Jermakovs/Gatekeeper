from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.schemas.token_check import TokenCheckSchema
from typing import Annotated
from src.services.tokens.access.verify_access_token import verify_access_token
from sqlmodel.ext.asyncio.session import AsyncSession
from src.config.db_dependency import get_db
from src.services.tokens.access.refresh_access_token import refresh_access_token
from src.schemas.token import Token as TokenSchema

# Router objekta izveide
router = APIRouter(
    prefix="/token",
    tags=["Tokens check and refresh service"]
)

# Drošības shēmas
refresh_scheme = HTTPBearer()   # refresh token
access_scheme = HTTPBearer()    # access token


# Access tokena pārbaudes endpoint
@router.get("/verify", response_model=TokenCheckSchema)
async def check_token_endpoint(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(access_scheme)],
):
    access_token = credentials.credentials
    
    payload = await verify_access_token(
        token=access_token,
    )

    return TokenCheckSchema(
        access_token=access_token,
    )


# Tokenu atjaunošana
@router.post("/refresh", response_model=TokenSchema)
async def refresh_token_endpoint(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(refresh_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    refresh_token = credentials.credentials
    return await refresh_access_token(refresh_token, db)