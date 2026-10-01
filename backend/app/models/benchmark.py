from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Float, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mode: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    iterations: Mapped[int] = mapped_column(Integer, nullable=False)
    payload_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    keygen_ms: Mapped[float] = mapped_column(Float, nullable=False)
    encapsulation_ms: Mapped[float] = mapped_column(Float, nullable=False)
    encryption_ms: Mapped[float] = mapped_column(Float, nullable=False)
    signing_ms: Mapped[float] = mapped_column(Float, nullable=False)
    verification_ms: Mapped[float] = mapped_column(Float, nullable=False)
    decapsulation_ms: Mapped[float] = mapped_column(Float, nullable=False)
    decryption_ms: Mapped[float] = mapped_column(Float, nullable=False)
    total_ms: Mapped[float] = mapped_column(Float, nullable=False)
    package_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
