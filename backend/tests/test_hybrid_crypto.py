import copy

from app.crypto.hybrid import CryptoPackageError, HybridCryptoService


def test_hybrid_round_trip() -> None:
    service = HybridCryptoService()
    package = service.encrypt(b"temperature=24.5C", b"sensor=v1", "sensor-001")

    assert service.decrypt(package) == b"temperature=24.5C"
    assert package["classical_kem"] == "X25519"
    assert package["pqc_kem"] == "ML-KEM-768"
    assert package["aead"] == "AES-256-GCM"
    assert package["signature"] == "ML-DSA-65"


def test_tampering_is_rejected_before_decryption() -> None:
    service = HybridCryptoService()
    package = service.encrypt(b"normal device telemetry")
    tampered = copy.deepcopy(package)
    tampered["ciphertext"] = tampered["ciphertext"][:-2] + ("AA" if tampered["ciphertext"][-2:] != "AA" else "BB")

    try:
        service.decrypt(tampered)
    except CryptoPackageError as error:
        assert "signature" in str(error).lower()
    else:
        raise AssertionError("Tampered package was accepted")


def test_wrong_service_cannot_decrypt() -> None:
    sender = HybridCryptoService()
    receiver = HybridCryptoService()
    package = sender.encrypt(b"secret")

    try:
        receiver.decrypt(package)
    except CryptoPackageError:
        pass
    else:
        raise AssertionError("A different key identity decrypted the package")


def test_public_metadata_contains_no_private_keys() -> None:
    service = HybridCryptoService()
    metadata = service.public_metadata()
    assert "x25519_private_key" not in metadata
    assert "mlkem_private_key" not in metadata
    assert "mldsa_private_key" not in metadata
