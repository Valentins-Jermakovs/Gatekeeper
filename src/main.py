# ==========================================
#                   imports
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from utils.init_db import init_db
from api import main_router
# ==========================================


# ==========================================
#                   main
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

# FastAPI objekta izveide
app = FastAPI(lifespan=lifespan)
# Nolasa .env faila saturu
load_dotenv()

# Routers
app.include_router(main_router)
# ==========================================