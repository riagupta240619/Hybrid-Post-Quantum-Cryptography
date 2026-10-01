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


def test_mqtt_gateway_accepts_and_decrypts_valid_package(monkeypatch) -> None:
    import json
    from collections import deque
    from types import SimpleNamespace

    from app.api.v1.crypto import crypto_service

    monkeypatch.setattr(mqtt_gateway, "_messages", deque(maxlen=100))
    package = crypto_service.encrypt(
        json.dumps({"temperature_c": 24.5}, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        b"temperature-sensor-001",
        "temperature-sensor-001",
    )
    message = SimpleNamespace(
        topic="pqshield/temperature-sensor-001/telemetry",
        payload=json.dumps(package, sort_keys=True, separators=(",", ":")).encode("utf-8"),
    )

    mqtt_gateway._on_message(None, None, message)

    event = mqtt_gateway.recent_messages()[0]
    assert event["device_id"] == "temperature-sensor-001"
    assert event["security"]["verified"] is True
    assert event["telemetry"]["temperature_c"] == 24.5
    assert "error" not in event


def test_mqtt_gateway_rejects_tampered_package(monkeypatch) -> None:
    import copy
    import json
    from collections import deque
    from types import SimpleNamespace

    from app.api.v1.crypto import crypto_service

    monkeypatch.setattr(mqtt_gateway, "_messages", deque(maxlen=100))
    package = crypto_service.encrypt(
        b'{"temperature_c":24.5}',
        b"temperature-sensor-001",
        "temperature-sensor-001",
    )
    tampered = copy.deepcopy(package)
    tampered["ciphertext"] = tampered["ciphertext"][:-2] + (
        "AA" if tampered["ciphertext"][-2:] != "AA" else "BB"
    )
    message = SimpleNamespace(
        topic="pqshield/temperature-sensor-001/telemetry",
        payload=json.dumps(tampered, sort_keys=True, separators=(",", ":")).encode("utf-8"),
    )

    mqtt_gateway._on_message(None, None, message)

    event = mqtt_gateway.recent_messages()[0]
    assert event["security"]["verified"] is False
    assert "signature" in event["error"].lower()
