from fastapi.testclient import TestClient

from app.api.v1.iot import mqtt_gateway
from app.main import create_app
from app.core.config import Settings


def test_iot_publish_uses_hybrid_crypto_and_mqtt(monkeypatch) -> None:
    monkeypatch.setattr(mqtt_gateway, "_connected", True)
    published: list[tuple[str, dict]] = []

    def fake_publish(device_id: str, package: dict) -> None:
        published.append((device_id, package))

    monkeypatch.setattr(mqtt_gateway, "publish", fake_publish)

    app = create_app(
        Settings(
            app_env="test",
            database_url="sqlite+pysqlite:///:memory:",
            frontend_origin="http://testserver",
        )
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/iot/publish",
            json={
                "device_id": "temperature-sensor-001",
                "telemetry": {"temperature_c": 24.5, "battery_percent": 91},
                "associated_data": "temperature-sensor-001",
            },
        )

    assert response.status_code == 202
    assert published[0][0] == "temperature-sensor-001"
    package = published[0][1]
    assert package["pqc_kem"] == "ML-KEM-768"
    assert package["signature"] == "ML-DSA-65"
    assert package["aead"] == "AES-256-GCM"
