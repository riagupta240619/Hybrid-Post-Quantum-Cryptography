from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DeviceCreate(BaseModel):
    device_id: str = Field(min_length=1, max_length=128)
    device_type: str = Field(min_length=1, max_length=64)

    @field_validator("device_id", "device_type")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Value must contain at least one non-whitespace character")
        return normalized


class DeviceRead(BaseModel):
    id: int
    device_id: str
    device_type: str
    status: str
    created_at: datetime
    last_seen: datetime | None

    model_config = ConfigDict(from_attributes=True)