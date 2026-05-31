# Tiek importētas nepieciešamas bibliotēkas
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


# =====================================================
# Ielādē dotenv failu, lai varētu izmantot DATABASE_URL
# =====================================================

load_dotenv()                               # Ielādē dotenv failu
DATABASE_URL = os.getenv("DATABASE_URL")    # Nolasa ceļu līdz DB

engine = create_async_engine(
    DATABASE_URL,
    echo=True,          # parāda SQL (dev vajadzībām)
)

# Izveido sesijas fabriku (Asinhroni)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)