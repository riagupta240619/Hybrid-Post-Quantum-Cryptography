import json
import pytest
from app.crypto.device_identity import DeviceCryptoError, DeviceCryptoRegistry

def test_device_identity_round_trip():
    registry=DeviceCryptoRegistry(); registry.provision("sensor-a"); registry.provision("pqshield-gateway")
    package=registry.encrypt_for("sensor-a","pqshield-gateway",json.dumps({"temperature_c":24.5}).encode(),sequence=7)
    plaintext=registry.decrypt_for("pqshield-gateway",package)
    assert json.loads(plaintext)=={"temperature_c":24.5}
    assert package["signature"]=="ML-DSA-65"
    assert package["pqc_kem"]=="ML-KEM-768"

def test_private_keys_are_not_in_public_metadata():
    registry = DeviceCryptoRegistry()
    registry.provision("sensor-a")

    metadata = registry.public_metadata("sensor-a")

    assert metadata["private_keys_exposed"] is False
    assert metadata["key_storage"] == "process-memory"

    # Public metadata may describe private-key handling,
    # but must not contain actual private-key material.
    assert "x25519_private_key" not in metadata
    assert "mlkem_private_key" not in metadata
    assert "mldsa_private_key" not in metadata

    serialized = json.dumps(metadata).lower()
    assert "private_key_material" not in serialized

def test_unknown_sender_is_rejected():
    registry=DeviceCryptoRegistry(); registry.provision("gateway"); registry.provision("sender")
    package=registry.encrypt_for("sender","gateway",b"hello",sequence=1)
    fresh=DeviceCryptoRegistry(); fresh.provision("gateway")
    with pytest.raises(DeviceCryptoError): fresh.decrypt_for("gateway",package)
