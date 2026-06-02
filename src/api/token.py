# =========================================================================
#                               imports
# =========================================================================
# Libraries:
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
# Dependencies:
from config.db_dependency import get_db
# Services:
import services.tokens.token_service as token
# Schemas:
from schemas import TokenResponse, RefreshRequest
# =========================================================================


# =========================================================================
#                       Router + Security Schemas
# =========================================================================

# Router object
router = APIRouter(
    prefix="/token",
    tags=["Tokens check and refresh service"]
)

# Security Schemas
access_scheme = HTTPBearer()    # access token


# =========================================================================
#                             Endpoints
# =========================================================================

# ================= Tokens refresh endpoint ===========================
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(
    data: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):

    return await token.refresh_access_token(
        refresh_token=data.refresh_token,
        db=db
    )