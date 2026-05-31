from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from utils.init_db import init_db
from routers import auth_route, verify_route


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
load_dotenv()


app.include_router(auth_route.router)
app.include_router(verify_route.router)