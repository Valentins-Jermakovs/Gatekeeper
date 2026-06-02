# =========================================================================
#                               imports
# =========================================================================
# Libraries:
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
# Dependencies:
from config.current_user import get_current_user
from config.db_dependency import get_db
# Schemas:
from schemas import UserResponse
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

    return await user_service.get_user_info(user_id=user_id, user_roles=user_roles, db=db)
# =========================================================================