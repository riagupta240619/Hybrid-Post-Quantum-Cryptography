from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import engine


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        if app_settings.app_env != "test":
            Base.metadata.create_all(bind=engine)
        yield

    application = FastAPI(
        title="PQShield API",
        version=app_settings.app_version,
        description="Phase 1 device registry API. Cryptographic functionality is not implemented.",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    application.include_router(api_router)
    return application


app = create_app()