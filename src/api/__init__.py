# =====================================================
#                   imports
# =====================================================
from fastapi import APIRouter
from .auth import router as auth_route
from .verify import router as verify_route
# =====================================================


# =====================================================
#                   Router objekts
# =====================================================
main_router = APIRouter()
main_router.include_router(auth_route)
main_router.include_router(verify_route)
# =====================================================