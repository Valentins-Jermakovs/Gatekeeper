# =====================================================
#                   imports
# =====================================================
from fastapi import APIRouter
from .auth import router as auth_route
from .token import router as token_route
from .metrics import router as metrics_route
from .users import router as users_route
# =====================================================


# =====================================================
#               Router object and includes
# =====================================================
main_router = APIRouter()
main_router.include_router(auth_route)
main_router.include_router(token_route)
main_router.include_router(metrics_route)
main_router.include_router(users_route)
# =====================================================