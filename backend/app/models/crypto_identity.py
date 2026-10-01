from datetime import datetime
from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class DeviceCryptoIdentity(Base):
    __tablename__ = "device_crypto_identities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    x25519_public_key: Mapped[str] = mapped_column(String(256), nullable=False)
    mlkem_public_key: Mapped[str] = mapped_column(String(4096), nullable=False)
    mldsa_public_key: Mapped[str] = mapped_column(String(8192), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
