# =====================================================
#                       imports
# =====================================================
from .database import AsyncSessionLocal
# =====================================================

# =====================================================
# Asinhronas sesijas izveide
# =====================================================
async def get_db():
    async with AsyncSessionLocal() as session:           # Izveido sesiju
        yield session                                    # Atgriež sesiju