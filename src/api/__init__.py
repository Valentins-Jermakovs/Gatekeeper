# =====================================================
#                   imports
# =====================================================
from fastapi import APIRouter
from .auth import router as auth_route
from .verify import router as verify_route
from .metrics import router as metrics_route
# =====================================================


# =====================================================
#               Router object and includes
# =====================================================
main_router = APIRouter()
main_router.include_router(auth_route)
main_router.include_router(verify_route)
main_router.include_router(metrics_route)
# =====================================================