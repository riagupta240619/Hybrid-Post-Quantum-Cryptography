def test_crypto_api_round_trip(client) -> None:
    encrypted = client.post(
        "/api/v1/crypto/encrypt",
        json={
            "plaintext": "temperature=24.5C",
            "device_id": "sensor-001",
            "associated_data": "sensor=v1",
        },
    )

    assert encrypted.status_code == 200
    package = encrypted.json()["package"]

    info = client.get("/api/v1/crypto/info")
    assert info.status_code == 200
    assert info.json()["pqc_kem"] == "ML-KEM-768"
    assert info.json()["signature"] == "ML-DSA-65"

    decrypted = client.post("/api/v1/crypto/decrypt", json={"package": package})
    assert decrypted.status_code == 200
    assert decrypted.json()["plaintext"] == "temperature=24.5C"


def test_crypto_api_rejects_tampering(client) -> None:
    encrypted = client.post(
        "/api/v1/crypto/encrypt",
        json={"plaintext": "normal telemetry"},
    )
    package = encrypted.json()["package"]
    package["device_id"] = "modified-device"

    decrypted = client.post("/api/v1/crypto/decrypt", json={"package": package})
    assert decrypted.status_code == 400
    assert "signature" in decrypted.json()["detail"].lower()
