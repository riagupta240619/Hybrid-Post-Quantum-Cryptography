from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db_session
from app.models import BenchmarkRun
from app.schemas.security import BenchmarkRequest, BenchmarkResponse, BenchmarkResult
from app.services.benchmark import BenchmarkService

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])
service = BenchmarkService()

@router.post("/run", response_model=BenchmarkResponse)
def run_benchmark(request: BenchmarkRequest, session: Session = Depends(get_db_session)) -> BenchmarkResponse:
    results = service.run(request.iterations, request.payload_bytes)
    rows=[]
    for r in results:
        row=BenchmarkRun(mode=r.mode, iterations=r.iterations, payload_bytes=r.payload_bytes, keygen_ms=r.keygen_ms, encapsulation_ms=r.encapsulation_ms, encryption_ms=r.encryption_ms, signing_ms=r.signing_ms, verification_ms=r.verification_ms, decapsulation_ms=r.decapsulation_ms, decryption_ms=r.decryption_ms, total_ms=r.total_ms, package_bytes=r.package_bytes, notes="Median per-operation timings measured with time.perf_counter_ns")
        session.add(row); rows.append(row)
    session.commit()
    return BenchmarkResponse(run_id=rows[0].id, results=[BenchmarkResult(**r.__dict__) for r in results], created_at=datetime.now(timezone.utc))

@router.get("/history")
def benchmark_history(limit: int = 50, session: Session = Depends(get_db_session)) -> list[dict[str, object]]:
    rows=session.query(BenchmarkRun).order_by(BenchmarkRun.created_at.desc()).limit(max(1,min(limit,200))).all()
    return [{"id":r.id,"mode":r.mode,"iterations":r.iterations,"payload_bytes":r.payload_bytes,"total_ms":r.total_ms,"package_bytes":r.package_bytes,"created_at":r.created_at} for r in rows]
