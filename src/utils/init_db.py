# Importē bibliotēkas, modeļus, utilītas
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os
from models import UserRoles, RefreshToken, User, Role
from utils.init_db_roles import init_roles

# Ielādē dotenv failu, lai varētu izmantot DATABASE_URL
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Dziņa izveide
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

# DB inicializācija
async def init_db():

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Lomas inicializēšana
    await init_roles(engine)