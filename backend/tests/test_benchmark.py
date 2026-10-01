from app.services.benchmark import BenchmarkService

def test_benchmark_returns_all_modes():
    results=BenchmarkService().run(iterations=3,payload_bytes=64)
    assert {r.mode for r in results}=={"classical","pqc","hybrid"}
    for result in results:
        assert result.total_ms >= 0
        assert result.package_bytes > 0
        assert result.payload_bytes == 64
