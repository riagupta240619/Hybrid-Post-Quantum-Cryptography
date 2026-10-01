from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class CryptoIdentityRead(BaseModel):
    device_id: str
    version: int
    classical_kem: str
    pqc_kem: str
    aead: str
    signature: str
    kdf: str
    x25519_public_key: str
    mlkem_public_key: str
    mldsa_public_key: str
    private_keys_exposed: bool
    key_storage: str

class SecurityEventRead(BaseModel):
    id: int
    device_id: str | None
    event_type: str
    result: str
    verified: bool
    sequence: int | None
    details: dict[str, Any]
    created_at: datetime

class AuditLogRead(BaseModel):
    id: int
    action: str
    actor: str
    device_id: str | None
    details: dict[str, Any]
    created_at: datetime

class BenchmarkRequest(BaseModel):
    iterations: int = Field(default=25, ge=3, le=500)
    payload_bytes: int = Field(default=1024, ge=16, le=65536)

class BenchmarkResult(BaseModel):
    mode: str
    iterations: int
    payload_bytes: int
    keygen_ms: float
    encapsulation_ms: float
    encryption_ms: float
    signing_ms: float
    verification_ms: float
    decapsulation_ms: float
    decryption_ms: float
    total_ms: float
    package_bytes: int

class BenchmarkResponse(BaseModel):
    run_id: int
    results: list[BenchmarkResult]
    created_at: datetime
