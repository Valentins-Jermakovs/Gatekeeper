# =====================================================
#                       imports
# =====================================================
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
# =====================================================


# =====================================================
# Ielādē dotenv failu, lai varētu izmantot DATABASE_URL
# =====================================================
load_dotenv()                               # Ielādē dotenv failu
DATABASE_URL = os.getenv("DATABASE_URL")    # Nolasa ceļu līdz DB
# =====================================================


# =====================================================
#                   Dziņa izveide
# =====================================================
engine = create_async_engine(
    DATABASE_URL,       # Dziņa URL
    echo=True,          # parāda SQL (dev vajadzībām)
)

# =====================================================
#           Asinhronas sesijas izveide
# =====================================================
# Izveido sesijas fabriku (Asinhroni)
AsyncSessionLocal = sessionmaker(
    engine,                         # Dziņa objekts
    class_=AsyncSession,            # Asinhrona sesija
    expire_on_commit=False          # Sesija nebeidzas pēc saglabāšanas
)