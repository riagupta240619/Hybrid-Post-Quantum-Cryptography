# PQShield Architecture — Phase 3

Phase 3 keeps the Phase 2 hybrid cryptographic boundary and adds an MQTT transport and IoT gateway.

## End-to-end flow

1. A virtual IoT device creates telemetry.
2. The simulator requests a hybrid encrypted package from the PQShield crypto API.
3. The API uses X25519 + ML-KEM-768, HKDF-SHA384, AES-256-GCM, and ML-DSA-65.
4. The simulator publishes the resulting package to `pqshield/<device_id>/telemetry` using MQTT QoS 1.
5. Mosquitto transports the package without needing to understand its cryptographic contents.
6. The PQShield MQTT gateway subscribes to the telemetry topic.
7. The gateway verifies the ML-DSA signature before decrypting the AES-GCM payload.
8. Successfully decrypted telemetry is retained in a bounded in-memory recent-message buffer for API inspection.

## Components

```text
+---------------------+
| Virtual IoT Device  |
+----------+----------+
           |
           | encrypted package
           v
+---------------------+
| Mosquitto MQTT      |
| pqshield/+/telemetry|
+----------+----------+
           |
           v
+---------------------+
| PQShield Gateway    |
| ML-DSA verify       |
| X25519 + ML-KEM     |
| AES-256-GCM decrypt |
+----------+----------+
           |
           v
+---------------------+
| Recent telemetry    |
| API view            |
+---------------------+
```

## MQTT topic model

The gateway subscribes to:

```text
pqshield/+/telemetry
```

A device publishes to:

```text
pqshield/<device_id>/telemetry
```

The MQTT message itself is a JSON-encoded Phase 2 cryptographic package.

## Trust boundary

The MQTT broker is a transport component. It does not provide application-level confidentiality or authenticity for the telemetry package. Those properties are supplied by the PQShield cryptographic package.

For local development, Mosquitto allows anonymous connections. This is deliberately limited to the research/demo environment. A production deployment should add TLS, authentication, topic ACLs, device identities, replay protection, and external key management.

## Simulator limitation

The Phase 3 simulator calls the PQShield crypto API before publishing. This is intentionally simple and reproducible. It demonstrates encrypted IoT transport and gateway processing without pretending that independent device provisioning has already been solved.

A future device-identity phase should provision each device with its own signing/key-establishment identity and remove the simulator's dependency on the central crypto API.

## Key lifecycle

The Phase 2 in-memory key lifecycle remains unchanged. Restarting the backend creates a new cryptographic identity, so packages created under an older backend process are not expected to decrypt after restart.

## Scope

Phase 3 does not claim a standardized MQTT security protocol or production deployment. It is an academic integration layer showing how the hybrid cryptographic package can travel through an IoT messaging system.
