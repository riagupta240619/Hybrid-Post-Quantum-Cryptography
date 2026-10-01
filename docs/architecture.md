# PQShield Architecture — Phase 2

Phase 2 preserves the Phase 1 API/service/database separation and adds a dedicated cryptographic boundary under backend/app/crypto/.

## Hybrid encryption flow

1. The sender creates an ephemeral X25519 key pair.
2. X25519 derives a classical shared secret with the recipient's X25519 public key.
3. ML-KEM-768 encapsulates against the recipient's ML-KEM public key and produces a post-quantum shared secret plus KEM ciphertext.
4. HKDF-SHA384 combines X25519_shared_secret || ML-KEM_shared_secret into a 32-byte AES key.
5. AES-256-GCM encrypts the plaintext with a fresh 96-bit nonce and canonical associated data.
6. The resulting package, including the ciphertext and algorithm identifiers, is signed with ML-DSA-65.
7. Decryption verifies the ML-DSA signature before key derivation and AES-GCM decryption.

## Package structure

```text
version
algorithm identifiers
device identifier
ephemeral X25519 public key
ML-KEM ciphertext
AES-GCM nonce
associated data
AES-GCM ciphertext + authentication tag
ML-DSA signature
```

The package is canonicalized as JSON using sorted keys and compact separators before signing. This makes the signed byte sequence deterministic.

## Key lifecycle in Phase 2

The backend generates one in-memory recipient X25519/ML-KEM identity and one ML-DSA signing identity when the crypto service is created. Private keys are not persisted in PostgreSQL and are never returned through /crypto/info.

Restarting the backend generates a new identity, so encrypted packages from a previous process should not be expected to decrypt after restart.

## Security boundary

The project does not implement ML-KEM or ML-DSA itself. It delegates those algorithms to pqcrypto and delegates X25519, HKDF, and AES-GCM to cryptography.

This construction is for an academic platform and is not a claim of production protocol standardization or certification.
