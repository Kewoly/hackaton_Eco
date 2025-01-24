from contextlib import asynccontextmanager
from config import Config
from fastapi import FastAPI
from pymongo import MongoClient

from routes.router import router
config = Config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for database connection"""
    yield
    print("API started !")

app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/api")