# ==========================================
#                   imports
# ==========================================
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from utils.init_db import init_db
from api import main_router
from starlette.middleware.sessions import SessionMiddleware
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

secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    raise RuntimeError("SECRET_KEY environment variable is required for session middleware")

app.add_middleware(SessionMiddleware, secret_key=secret_key)

# Routers
app.include_router(main_router)
# ==========================================