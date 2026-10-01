from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.api.v1.router import api_router
from app.api.v1.iot import mqtt_gateway
from app.core.config import Settings, get_settings
from app.crypto.device_identity import registry
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Device

GATEWAY_ID = "pqshield-gateway"

def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        if app_settings.app_env != "test":
            Base.metadata.create_all(bind=engine)
            registry.ensure(GATEWAY_ID)
            if app_settings.mqtt_enabled:
                mqtt_gateway.start()
        try:
            yield
        finally:
            if app_settings.app_env != "test" and app_settings.mqtt_enabled:
                mqtt_gateway.stop()
    application = FastAPI(title="PQShield API", version=app_settings.app_version, description="Hybrid post-quantum security platform for IoT and cloud environments.", lifespan=lifespan)
    application.add_middleware(CORSMiddleware, allow_origins=app_settings.cors_origins, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
    application.include_router(api_router)
    return application

app = create_app()
