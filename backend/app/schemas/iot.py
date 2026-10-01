from typing import Any

from pydantic import BaseModel, Field


class IotPublishRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=128)
    telemetry: dict[str, Any]
    associated_data: str = Field(default="", max_length=4096)
    sequence: int = Field(ge=0)


class IotPublishResponse(BaseModel):
    device_id: str
    topic: str
    security: dict[str, str]
    package: dict[str, Any]


class IotMessage(BaseModel):
    device_id: str | None = None
    topic: str
    received_at: str
    telemetry: dict[str, Any] | None = None
    security: dict[str, Any]
    error: str | None = None
