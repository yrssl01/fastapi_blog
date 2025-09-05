from src.logger import logger
from src.core.database import engine, Base
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from src.api.routes import main_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict, None]:
    logger.info("Starting up...")
    yield
    logger.info("Shutting down...")



app = FastAPI(
    title="FastAPI Blog Project",
    description="A simple blog project using FastAPI",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(main_router)


app.mount(
    "/static",
    StaticFiles(directory="src/static"),
    name="static"
)


@app.post("/")
async def setup_database():
    logger.info("Setting up the database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)