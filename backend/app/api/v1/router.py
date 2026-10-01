from fastapi import APIRouter
from app.api.v1.benchmarks import router as benchmarks_router
from app.api.v1.crypto import router as crypto_router
from app.api.v1.devices import router as devices_router
from app.api.v1.health import router as health_router
from app.api.v1.iot import router as iot_router
from app.api.v1.security import router as security_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(devices_router)
api_router.include_router(crypto_router)
api_router.include_router(iot_router)
api_router.include_router(security_router)
api_router.include_router(benchmarks_router)
