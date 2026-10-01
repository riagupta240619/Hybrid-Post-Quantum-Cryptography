from __future__ import annotations

import base64
import json
import os
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


class CryptoPackageError(ValueError):
    """Raised when an encrypted package is malformed or cannot be authenticated."""


class HybridCryptoService:
    """In-memory Phase 2 hybrid crypto provider.

    This is deliberately a small research/demo boundary. It combines X25519 and
    ML-KEM-768 through HKDF-SHA384, uses AES-256-GCM for payload encryption, and
    authenticates the canonical package with ML-DSA-65.

    Private key material is intentionally kept only in memory in this phase.
    Restarting the backend creates a new recipient/signing identity, so packages
    from a previous process are not expected to decrypt after a restart.
    """

    VERSION = 1
    CLASSICAL_KEM = "X25519"
    PQ_KEM = "ML-KEM-768"
    AEAD = "AES-256-GCM"
    SIGNATURE = "ML-DSA-65"
    KDF = "HKDF-SHA384"
    INFO = b"PQShield hybrid key combiner v1"

    def __init__(self) -> None:
        self._x25519_private = X25519PrivateKey.generate()
        self._x25519_public = self._x25519_private.public_key()
        self._mlkem_public, self._mlkem_private = kem_keygen()
        self._mldsa_public, self._mldsa_private = sig_keygen()

    @staticmethod
    def _b64(value: bytes) -> str:
        return base64.b64encode(value).decode("ascii")

    @staticmethod
    def _unb64(value: str) -> bytes:
        try:
            return base64.b64decode(value.encode("ascii"), validate=True)
        except (ValueError, UnicodeEncodeError) as error:
            raise CryptoPackageError("Invalid base64 field") from error

    @staticmethod
    def _canonical(value: dict[str, Any]) -> bytes:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    @staticmethod
    def _derive_key(classical_secret: bytes, pq_secret: bytes) -> bytes:
        return HKDF(
            algorithm=hashes.SHA384(),
            length=32,
            salt=None,
            info=HybridCryptoService.INFO,
        ).derive(classical_secret + pq_secret)

    def public_metadata(self) -> dict[str, Any]:
        """Return public algorithm/key metadata; never returns private key material."""
        return {
            "version": self.VERSION,
            "classical_kem": self.CLASSICAL_KEM,
            "pqc_kem": self.PQ_KEM,
            "aead": self.AEAD,
            "signature": self.SIGNATURE,
            "kdf": self.KDF,
            "x25519_public_key": self._b64(
                self._x25519_public.public_bytes(
                    serialization.Encoding.Raw,
                    serialization.PublicFormat.Raw,
                )
            ),
            "mlkem_public_key": self._b64(self._mlkem_public),
            "mldsa_public_key": self._b64(self._mldsa_public),
        }

    def encrypt(
        self,
        plaintext: bytes,
        associated_data: bytes = b"",
        device_id: str = "demo-device",
        sequence: int | None = None,
    ) -> dict[str, Any]:
        ephemeral_private = X25519PrivateKey.generate()
        ephemeral_public = ephemeral_private.public_key()
        classical_secret = ephemeral_private.exchange(self._x25519_public)
        kem_ciphertext, pq_secret = kem_encaps(self._mlkem_public)
        aes_key = self._derive_key(classical_secret, pq_secret)
        nonce = os.urandom(12)

        package: dict[str, Any] = {
            "version": self.VERSION,
            "device_id": device_id,
            "classical_kem": self.CLASSICAL_KEM,
            "pqc_kem": self.PQ_KEM,
            "kdf": self.KDF,
            "aead": self.AEAD,
            "signature": self.SIGNATURE,
            "ephemeral_x25519_public_key": self._b64(
                ephemeral_public.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
            ),
            "mlkem_ciphertext": self._b64(kem_ciphertext),
            "nonce": self._b64(nonce),
            "associated_data": self._b64(associated_data),
        }
        if sequence is not None:
            if sequence < 0:
                raise ValueError("sequence must be non-negative")
            package["sequence"] = sequence

        aad = self._canonical(package)
        ciphertext = AESGCM(aes_key).encrypt(nonce, plaintext, aad)
        package["ciphertext"] = self._b64(ciphertext)
        signing_payload = self._canonical(package)
        package["signature_value"] = self._b64(sig_sign(self._mldsa_private, signing_payload))
        return package

    def decrypt(self, package: dict[str, Any]) -> bytes:
        required = {
            "version", "device_id", "classical_kem", "pqc_kem", "kdf", "aead", "signature",
            "ephemeral_x25519_public_key", "mlkem_ciphertext", "nonce", "associated_data",
            "ciphertext", "signature_value",
        }
        missing = required.difference(package)
        if missing:
            raise CryptoPackageError(f"Missing package fields: {', '.join(sorted(missing))}")
        if package["version"] != self.VERSION:
            raise CryptoPackageError("Unsupported package version")
        if package["classical_kem"] != self.CLASSICAL_KEM or package["pqc_kem"] != self.PQ_KEM:
            raise CryptoPackageError("Unsupported key establishment algorithms")
        if package["aead"] != self.AEAD or package["signature"] != self.SIGNATURE or package["kdf"] != self.KDF:
            raise CryptoPackageError("Unsupported cryptographic parameters")
        if "sequence" in package and (
            not isinstance(package["sequence"], int) or isinstance(package["sequence"], bool) or package["sequence"] < 0
        ):
            raise CryptoPackageError("Invalid replay-protection sequence")

        signature = self._unb64(package["signature_value"])
        signed_package = dict(package)
        signed_package.pop("signature_value")
        try:
            sig_verify(self._mldsa_public, self._canonical(signed_package), signature)
        except Exception as error:
            raise CryptoPackageError("ML-DSA signature verification failed") from error

        ephemeral_public = X25519PublicKey.from_public_bytes(self._unb64(package["ephemeral_x25519_public_key"]))
        classical_secret = self._x25519_private.exchange(ephemeral_public)
        pq_secret = kem_decaps(self._mlkem_private, self._unb64(package["mlkem_ciphertext"]))
        aes_key = self._derive_key(classical_secret, pq_secret)
        nonce = self._unb64(package["nonce"])
        ciphertext = self._unb64(package["ciphertext"])
        associated_data = self._unb64(package["associated_data"])
        aad_package = dict(signed_package)
        aad_package.pop("ciphertext", None)
        aad = self._canonical(aad_package)
        try:
            return AESGCM(aes_key).decrypt(nonce, ciphertext, aad)
        except Exception as error:
            raise CryptoPackageError("AES-GCM authentication/decryption failed") from error
