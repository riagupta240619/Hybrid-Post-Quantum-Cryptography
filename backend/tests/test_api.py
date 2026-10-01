from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "pqshield", "version": "0.1.0"}


def test_create_and_retrieve_device(client: TestClient) -> None:
    created = client.post(
        "/api/v1/devices",
        json={"device_id": "sensor-001", "device_type": "temperature-sensor"},
    )

    assert created.status_code == 201
    assert created.json()["device_id"] == "sensor-001"
    assert created.json()["status"] == "offline"
    assert created.json()["last_seen"] is None

    retrieved = client.get("/api/v1/devices/sensor-001")

    assert retrieved.status_code == 200
    assert retrieved.json()["id"] == created.json()["id"]


def test_duplicate_device_id_is_rejected(client: TestClient) -> None:
    payload = {"device_id": "sensor-001", "device_type": "temperature-sensor"}
    assert client.post("/api/v1/devices", json=payload).status_code == 201

    duplicate = client.post("/api/v1/devices", json=payload)

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Device ID 'sensor-001' already exists"


def test_list_devices(client: TestClient) -> None:
    client.post("/api/v1/devices", json={"device_id": "sensor-001", "device_type": "temperature"})
    client.post("/api/v1/devices", json={"device_id": "sensor-002", "device_type": "humidity"})

    response = client.get("/api/v1/devices")

    assert response.status_code == 200
    assert {device["device_id"] for device in response.json()} == {"sensor-001", "sensor-002"}


def test_unknown_device_returns_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/devices/missing-device")

    assert response.status_code == 404