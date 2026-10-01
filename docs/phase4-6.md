# PQShield Phases 4–6

## Phase 4 — Platform security

### Device cryptographic identities
Each provisioned device receives an X25519 key pair, ML-KEM-768 key pair, and ML-DSA-65 key pair. PostgreSQL stores public-key metadata only. Private keys are held by the process-memory registry in this research build; restarting the backend invalidates active private identities and requires reprovisioning.

The identity-aware package contains sender and recipient identifiers, hybrid key-establishment material, AES-GCM payload data, and an ML-DSA signature. The MQTT gateway accepts this identity-aware format and verifies the sender before decryption.

### Persistent security events
Accepted and rejected MQTT decisions are persisted to security_events. Replay protection remains per-device and currently lives in gateway memory; a production version should persist sequence state or use a monotonic device counter backed by durable storage.

### Audit logs
Provisioning actions are stored in audit_logs and exposed through /api/v1/security/audit.

## Phase 5 — Cryptographic research benchmarks

The benchmark service measures three constructions using the same payload and iteration count:

1. Classical: X25519 + AES-256-GCM + Ed25519.
2. PQC: ML-KEM-768 + AES-256-GCM + ML-DSA-65.
3. Hybrid: X25519 + ML-KEM-768 + AES-256-GCM + ML-DSA-65.

Measured values include key generation, encapsulation, payload encryption, signing, verification, decapsulation, decryption, total median operation time, and package size.

Results are stored in benchmark_runs and exposed through /api/v1/benchmarks/run and /api/v1/benchmarks/history.

These measurements are machine-dependent and should be reported with hardware/software configuration in a research report.

## Phase 6 — Scalability and load testing

loadtests/locustfile.py provides a reproducible workload for health checks, crypto metadata, and encrypted IoT publishing. Docker Compose includes a loadtest profile with a conservative 10-user, 30-second default run.

Example:

    docker compose --profile loadtest run --rm loadtest

For larger experiments, run Locust externally or adjust the profile command and record user count, spawn rate, duration, CPU, memory, request rate, error rate, median latency, P95 latency, and P99 latency.

## Security and research notes

NIST finalized FIPS 203 for ML-KEM and FIPS 204 for ML-DSA in August 2024. PQShield uses ML-KEM-768 and ML-DSA-65 as concrete parameter sets. The hybrid combiner is a project-level construction and is not claimed to be a standardized interoperable wire protocol. Production deployment would require authenticated MQTT/TLS, durable key storage such as a KMS/HSM/Vault integration, key rotation, access control, and independent cryptographic review.
