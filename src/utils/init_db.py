# =====================================================
#                       imports
# =====================================================
# Libraries:
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os
# Models:
from models import UserRoles, RefreshToken, User, Role
# Utils:
from utils.init_db_roles import init_roles
# =====================================================


# =====================================================
#                   .env initialization
# =====================================================

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

# =====================================================
#                   DB initialization
# =====================================================

async def init_db():

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Initialize roles
    await init_roles(engine)