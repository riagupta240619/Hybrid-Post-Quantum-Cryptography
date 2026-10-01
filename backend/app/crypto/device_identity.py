from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from pqcrypto.kem.ml_kem_768 import decaps as kem_decaps
from pqcrypto.kem.ml_kem_768 import encaps as kem_encaps
from pqcrypto.kem.ml_kem_768 import keygen as kem_keygen
from pqcrypto.sign.ml_dsa_65 import keygen as sig_keygen
from pqcrypto.sign.ml_dsa_65 import sign as sig_sign
from pqcrypto.sign.ml_dsa_65 import verify as sig_verify

class DeviceCryptoError(ValueError):
    pass

@dataclass
class Identity:
    x_private: X25519PrivateKey
    x_public: bytes
    kem_public: bytes
    kem_private: bytes
    sig_public: bytes
    sig_private: bytes

class DeviceCryptoRegistry:
    VERSION = 2
    CLASSICAL_KEM = "X25519"
    PQ_KEM = "ML-KEM-768"
    AEAD = "AES-256-GCM"
    SIGNATURE = "ML-DSA-65"
    KDF = "HKDF-SHA384"
    INFO = b"PQShield device hybrid key combiner v2"

    def __init__(self) -> None:
        self._identities: dict[str, Identity] = {}

    @staticmethod
    def _b64(value: bytes) -> str:
        return base64.b64encode(value).decode("ascii")

    @staticmethod
    def _unb64(value: str) -> bytes:
        try:
            return base64.b64decode(value.encode("ascii"), validate=True)
        except (ValueError, UnicodeEncodeError) as error:
            raise DeviceCryptoError("Invalid base64 field") from error

    @staticmethod
    def _canonical(value: dict[str, Any]) -> bytes:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    @classmethod
    def _derive(cls, classical: bytes, pq: bytes) -> bytes:
        return HKDF(algorithm=hashes.SHA384(), length=32, salt=None, info=cls.INFO).derive(classical + pq)

    def provision(self, device_id: str) -> dict[str, Any]:
        if not device_id or not device_id.strip():
            raise DeviceCryptoError("device_id is required")
        x_private = X25519PrivateKey.generate()
        x_public = x_private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        kem_public, kem_private = kem_keygen()
        sig_public, sig_private = sig_keygen()
        self._identities[device_id] = Identity(x_private, x_public, kem_public, kem_private, sig_public, sig_private)
        return self.public_metadata(device_id)

    def ensure(self, device_id: str) -> dict[str, Any]:
        return self.public_metadata(device_id) if device_id in self._identities else self.provision(device_id)

    def has_private_identity(self, device_id: str) -> bool:
        return device_id in self._identities

    def public_metadata(self, device_id: str) -> dict[str, Any]:
        identity = self._identities.get(device_id)
        if identity is None:
            raise DeviceCryptoError(f"No active private identity for {device_id}")
        return {
            "version": self.VERSION,
            "device_id": device_id,
            "classical_kem": self.CLASSICAL_KEM,
            "pqc_kem": self.PQ_KEM,
            "aead": self.AEAD,
            "signature": self.SIGNATURE,
            "kdf": self.KDF,
            "x25519_public_key": self._b64(identity.x_public),
            "mlkem_public_key": self._b64(identity.kem_public),
            "mldsa_public_key": self._b64(identity.sig_public),
            "private_keys_exposed": False,
            "key_storage": "process-memory",
        }

    def export_public(self, device_id: str) -> dict[str, str]:
        meta = self.public_metadata(device_id)
        return {k: str(v) for k, v in meta.items() if k.endswith("public_key")}

    def encrypt_for(self, sender_id: str, recipient_id: str, plaintext: bytes, associated_data: bytes = b"", sequence: int | None = None) -> dict[str, Any]:
        sender = self._identities.get(sender_id)
        recipient = self._identities.get(recipient_id)
        if sender is None or recipient is None:
            raise DeviceCryptoError("Sender and recipient must both be provisioned in this process")
        recipient_x_public = X25519PublicKey.from_public_bytes(recipient.x_public)
        ephemeral = X25519PrivateKey.generate()
        classical_secret = ephemeral.exchange(recipient_x_public)
        kem_ciphertext, pq_secret = kem_encaps(recipient.kem_public)
        aes_key = self._derive(classical_secret, pq_secret)
        nonce = os.urandom(12)
        package: dict[str, Any] = {
            "version": self.VERSION,
            "device_id": sender_id,
            "sender_device_id": sender_id,
            "recipient_device_id": recipient_id,
            "classical_kem": self.CLASSICAL_KEM,
            "pqc_kem": self.PQ_KEM,
            "kdf": self.KDF,
            "aead": self.AEAD,
            "signature": self.SIGNATURE,
            "ephemeral_x25519_public_key": self._b64(ephemeral.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)),
            "mlkem_ciphertext": self._b64(kem_ciphertext),
            "nonce": self._b64(nonce),
            "associated_data": self._b64(associated_data),
        }
        if sequence is not None:
            if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
                raise DeviceCryptoError("sequence must be a non-negative integer")
            package["sequence"] = sequence
        aad = self._canonical(package)
        package["ciphertext"] = self._b64(AESGCM(aes_key).encrypt(nonce, plaintext, aad))
        signed = self._canonical(package)
        package["signature_value"] = self._b64(sig_sign(sender.sig_private, signed))
        return package

    def decrypt_for(self, recipient_id: str, package: dict[str, Any]) -> bytes:
        recipient = self._identities.get(recipient_id)
        if recipient is None:
            raise DeviceCryptoError(f"Recipient {recipient_id} is not provisioned")
        sender_id = str(package.get("sender_device_id") or package.get("device_id") or "")
        if package.get("recipient_device_id") != recipient_id:
            raise DeviceCryptoError("Package recipient does not match gateway identity")
        sender = self._identities.get(sender_id)
        if sender is None:
            raise DeviceCryptoError(f"Sender identity {sender_id} is unknown")
        required = {"version","sender_device_id","recipient_device_id","classical_kem","pqc_kem","kdf","aead","signature","ephemeral_x25519_public_key","mlkem_ciphertext","nonce","associated_data","ciphertext","signature_value"}
        missing = required.difference(package)
        if missing:
            raise DeviceCryptoError(f"Missing package fields: {', '.join(sorted(missing))}")
        if package["version"] != self.VERSION or package["classical_kem"] != self.CLASSICAL_KEM or package["pqc_kem"] != self.PQ_KEM or package["kdf"] != self.KDF or package["aead"] != self.AEAD or package["signature"] != self.SIGNATURE:
            raise DeviceCryptoError("Unsupported cryptographic parameters")
        if "sequence" in package and (not isinstance(package["sequence"], int) or isinstance(package["sequence"], bool) or package["sequence"] < 0):
            raise DeviceCryptoError("Invalid replay-protection sequence")
        signature = self._unb64(package["signature_value"])
        signed = dict(package)
        signed.pop("signature_value")
        try:
            sig_verify(sender.sig_public, self._canonical(signed), signature)
        except Exception as error:
            raise DeviceCryptoError("ML-DSA signature verification failed") from error
        ephemeral_public = X25519PublicKey.from_public_bytes(self._unb64(package["ephemeral_x25519_public_key"]))
        classical_secret = recipient.x_private.exchange(ephemeral_public)
        pq_secret = kem_decaps(recipient.kem_private, self._unb64(package["mlkem_ciphertext"]))
        aes_key = self._derive(classical_secret, pq_secret)
        nonce = self._unb64(package["nonce"])
        ciphertext = self._unb64(package["ciphertext"])
        aad = self._canonical({k: v for k, v in signed.items() if k != "ciphertext"})
        try:
            return AESGCM(aes_key).decrypt(nonce, ciphertext, aad)
        except Exception as error:
            raise DeviceCryptoError("AES-GCM authentication/decryption failed") from error

    def all_public_metadata(self) -> list[dict[str, Any]]:
        return [self.public_metadata(device_id) for device_id in sorted(self._identities)]

registry = DeviceCryptoRegistry()
