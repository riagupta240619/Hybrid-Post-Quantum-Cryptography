import copy
import json
from collections import deque
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.v1.iot import mqtt_gateway
from app.api.v1.crypto import crypto_service
from app.main import create_app
from app.core.config import Settings


def _message(package: dict) -> SimpleNamespace:
    return SimpleNamespace(
        topic=f"pqshield/{package['device_id']}/telemetry",
        payload=json.dumps(package, sort_keys=True, separators=(",", ":")).encode("utf-8"),
    )


def _reset_gateway_state() -> None:
    mqtt_gateway._messages = deque(maxlen=100)
    mqtt_gateway._highest_sequence = {}


def _package(device_id: str, sequence: int, temperature: float = 24.5) -> dict:
    return crypto_service.encrypt(
        json.dumps({"temperature_c": temperature}, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        device_id.encode("utf-8"),
        device_id,
        sequence,
    )


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
                "sequence": 1,
            },
        )

    assert response.status_code == 202
    assert published[0][0] == "temperature-sensor-001"
    package = published[0][1]
    assert package["pqc_kem"] == "ML-KEM-768"
    assert package["signature"] == "ML-DSA-65"
    assert package["aead"] == "AES-256-GCM"
    assert package["sequence"] == 1


def test_mqtt_gateway_accepts_and_decrypts_valid_package(monkeypatch) -> None:
    _reset_gateway_state()
    package = _package("temperature-sensor-001", 1)
    mqtt_gateway._on_message(None, None, _message(package))

    event = mqtt_gateway.recent_messages()[0]
    assert event["device_id"] == "temperature-sensor-001"
    assert event["security"]["verified"] is True
    assert event["security"]["sequence"] == 1
    assert event["telemetry"]["temperature_c"] == 24.5
    assert "error" not in event


def test_mqtt_gateway_rejects_tampered_package(monkeypatch) -> None:
    _reset_gateway_state()
    package = _package("temperature-sensor-001", 1)
    tampered = copy.deepcopy(package)
    tampered["ciphertext"] = tampered["ciphertext"][:-2] + (
        "AA" if tampered["ciphertext"][-2:] != "AA" else "BB"
    )

    mqtt_gateway._on_message(None, None, _message(tampered))

    event = mqtt_gateway.recent_messages()[0]
    assert event["security"]["verified"] is False
    assert "signature" in event["error"].lower()


def test_mqtt_gateway_rejects_exact_replay(monkeypatch) -> None:
    _reset_gateway_state()
    package = _package("temperature-sensor-001", 1)

    mqtt_gateway._on_message(None, None, _message(package))
    mqtt_gateway._on_message(None, None, _message(package))

    events = mqtt_gateway.recent_messages()
    assert events[0]["security"]["verified"] is False
    assert "replay detected" in events[0]["error"].lower()
    assert events[1]["security"]["verified"] is True


def test_mqtt_gateway_rejects_older_sequence(monkeypatch) -> None:
    _reset_gateway_state()
    mqtt_gateway._on_message(None, None, _message(_package("temperature-sensor-001", 5)))
    mqtt_gateway._on_message(None, None, _message(_package("temperature-sensor-001", 4)))

    event = mqtt_gateway.recent_messages()[0]
    assert event["security"]["verified"] is False
    assert "replay detected" in event["error"].lower()


def test_mqtt_gateway_accepts_newer_sequence(monkeypatch) -> None:
    _reset_gateway_state()
    mqtt_gateway._on_message(None, None, _message(_package("temperature-sensor-001", 5)))
    mqtt_gateway._on_message(None, None, _message(_package("temperature-sensor-001", 6)))

    events = mqtt_gateway.recent_messages()
    assert events[0]["security"]["verified"] is True
    assert events[0]["security"]["sequence"] == 6
    assert events[1]["security"]["sequence"] == 5


def test_mqtt_gateway_rejects_missing_sequence(monkeypatch) -> None:
    _reset_gateway_state()
    package = _package("temperature-sensor-001", 1)
    package_without_sequence = copy.deepcopy(package)
    package_without_sequence.pop("sequence")

    mqtt_gateway._on_message(None, None, _message(package_without_sequence))

    event = mqtt_gateway.recent_messages()[0]
    assert event["security"]["verified"] is False
    assert "sequence" in event["error"].lower()
