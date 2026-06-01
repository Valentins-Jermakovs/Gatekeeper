# =========================================================================
#                               imports
# =========================================================================
# Libraries:
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
# Dependencies:
from config.db_dependency import get_db
# Services:
import services.tokens.token_service as token
# Schemas:
from schemas import TokenResponse, TokenCheckResponse
# =========================================================================


# =========================================================================
#                       Router + Security Schemas
# =========================================================================

# Router object
router = APIRouter(
    prefix="/token",
    tags=["Tokens check and refresh service"]
)

# Drošības shēmas
refresh_scheme = HTTPBearer()   # refresh token
access_scheme = HTTPBearer()    # access token


# =========================================================================
#                             Endpoints
# =========================================================================

# ================= Access tokena verification endpoint ======================
@router.get("/verify", response_model=TokenCheckResponse)
async def check_token_endpoint(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(access_scheme)],
):
    access_token = credentials.credentials
    
    payload = await token.verify_access_token(
        token=access_token,
    )

    return TokenCheckResponse(
        access_token=access_token,
    )


# ================= Tokens refresh endpoint ===========================
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(refresh_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    refresh_token = credentials.credentials
    return await token.refresh_access_token(refresh_token, db)