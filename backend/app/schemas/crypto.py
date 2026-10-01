from typing import Any

from pydantic import BaseModel, Field


class EncryptRequest(BaseModel):
    plaintext: str = Field(min_length=1, max_length=1_000_000)
    device_id: str = Field(default="demo-device", min_length=1, max_length=128)
    associated_data: str = Field(default="", max_length=4_096)


class EncryptResponse(BaseModel):
    package: dict[str, Any]


class DecryptRequest(BaseModel):
    package: dict[str, Any]


class DecryptResponse(BaseModel):
    plaintext: str
