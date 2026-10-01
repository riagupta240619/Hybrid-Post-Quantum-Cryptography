# PQShield — Hybrid Post-Quantum Security Platform

> **Design and Implementation of a Hybrid Post-Quantum Encryption Layer for IoT and Cloud Environments**

PQShield is a software-based cybersecurity platform that demonstrates how **classical cryptography and post-quantum cryptography (PQC)** can be combined to protect data exchanged between simulated IoT devices and a secure gateway.

The platform combines **X25519 + ML-KEM-768** for hybrid key establishment, **HKDF-SHA384** for key derivation, **AES-256-GCM** for authenticated payload encryption, and **ML-DSA-65** for digital signatures.

---

## Table of Contents

- [Overview](#overview)
- [Objectives](#objectives)
- [Key Features](#key-features)
- [Cryptographic Architecture](#cryptographic-architecture)
- [End-to-End Data Flow](#end-to-end-data-flow)
- [IoT Security](#iot-security)
- [Platform Architecture](#platform-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Dashboard](#dashboard)
- [API](#api)
- [Benchmarking](#benchmarking)
- [Load Testing](#load-testing)
- [Installation and Setup](#installation-and-setup)
- [Testing](#testing)
- [Project Phases](#project-phases)
- [Security Considerations](#security-considerations)
- [Limitations](#limitations)
- [Future Scope](#future-scope)
- [Research Significance](#research-significance)

---

## Overview

Quantum computing presents a long-term challenge to public-key cryptography. PQShield explores a **hybrid migration approach** in which classical and post-quantum cryptographic mechanisms are used together.

The platform simulates an IoT environment containing devices such as:

- Temperature sensors
- Industrial sensors
- Vehicle telemetry devices
- Smart-home devices

Devices generate telemetry, protect it using the hybrid cryptographic layer, and transmit encrypted packages through MQTT to a PQShield gateway.

The gateway authenticates, decrypts, validates replay protection, and records security decisions.

---

## Objectives

The project aims to:

1. Implement a real software-based hybrid cryptographic layer.
2. Combine X25519 with ML-KEM-768 for key establishment.
3. Protect application payloads using AES-256-GCM.
4. Authenticate encrypted packages using ML-DSA-65.
5. Secure simulated IoT telemetry over MQTT.
6. Implement sequence-based replay protection.
7. Maintain persistent security and audit logs.
8. Provide an interactive web dashboard.
9. Compare classical, PQC, and hybrid cryptographic performance.
10. Evaluate the platform under increasing simulated workloads.

---

## Key Features

### Hybrid Cryptography

| Security Function | Algorithm |
|---|---|
| Classical Key Agreement | X25519 |
| Post-Quantum KEM | ML-KEM-768 |
| Key Derivation | HKDF-SHA384 |
| Payload Encryption | AES-256-GCM |
| Digital Signature | ML-DSA-65 |

### Device Cryptographic Identity

Each provisioned device can have:

- X25519 public key
- ML-KEM-768 public key
- ML-DSA-65 public key

Private key material is kept in process memory in the current research implementation.

### Secure MQTT Telemetry

Telemetry is encrypted before publication:

```
IoT Device
    |
    | Hybrid encrypted package
    v
MQTT Broker
    |
    v
PQShield Gateway
    |
    | Verify + Replay Check + Decrypt
    v
Verified Telemetry
```

### Replay Protection

Each telemetry package contains a sequence number.

For a device:

```
Sequence 1  -> ACCEPT
Sequence 2  -> ACCEPT
Sequence 3  -> ACCEPT
Sequence 3  -> BLOCK
Sequence 2  -> BLOCK
Sequence 4  -> ACCEPT
```

Replay state is maintained per device.

### Security Monitoring

The platform records:

- Accepted messages
- Rejected messages
- Signature failures
- Replay attempts
- Invalid packages
- Device security events

### Audit Logging

Important platform operations are persisted as audit records for investigation and demonstration purposes.

### Cryptographic Benchmarking

The platform compares:

- Classical cryptography
- Post-quantum cryptography
- Hybrid cryptography

Measured operations include key generation, encapsulation, encryption, signing, verification, decapsulation, decryption, total execution time, and package size.

### Load Testing

Locust is integrated for concurrent workload testing and IoT/API scalability experiments.

---

## Cryptographic Architecture

PQShield uses the following project-level hybrid construction:

```
             X25519 Shared Secret
                      |
                      |
             ML-KEM-768 Shared Secret
                      |
                      v
              Concatenate Secrets
                      |
                      v
                HKDF-SHA384
                      |
                      v
                AES-256-GCM Key
                      |
                      v
                 Ciphertext
                      |
                      v
                 ML-DSA-65
                   Signature
```

### Encryption

1. Generate an ephemeral X25519 key pair.
2. Perform X25519 key agreement with the recipient.
3. Encapsulate a shared secret using ML-KEM-768.
4. Combine both shared secrets using HKDF-SHA384.
5. Encrypt the payload using AES-256-GCM.
6. Construct the canonical encrypted package.
7. Sign the package using ML-DSA-65.

### Decryption

1. Validate the package structure and algorithm identifiers.
2. Verify the ML-DSA-65 signature.
3. Perform X25519 key agreement.
4. Decapsulate the ML-KEM-768 ciphertext.
5. Recreate the AES key using HKDF-SHA384.
6. Authenticate and decrypt using AES-256-GCM.
7. Apply sequence-based replay protection for IoT messages.

A modified package is rejected before plaintext is processed.

---

## End-to-End Data Flow

```
                    +----------------------+
                    |    Virtual Device    |
                    +----------+-----------+
                               |
                               | Telemetry
                               v
                    +----------------------+
                    | Hybrid Crypto Layer  |
                    | X25519               |
                    | ML-KEM-768           |
                    | HKDF-SHA384          |
                    | AES-256-GCM          |
                    | ML-DSA-65            |
                    +----------+-----------+
                               |
                               | Signed encrypted package
                               v
                    +----------------------+
                    |   MQTT / Mosquitto   |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |  PQShield Gateway    |
                    | Signature Verify     |
                    | Replay Protection    |
                    | Key Derivation       |
                    | AES-GCM Decryption   |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | PostgreSQL + API     |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | React Security UI    |
                    +----------------------+
```

---

## IoT Security

MQTT topics use the following convention:

```
pqshield/<device_id>/telemetry
```

Example telemetry:

```json
{
  "temperature_c": 24.7,
  "humidity_percent": 58.2,
  "battery_percent": 91.4,
  "sequence": 42
}
```

The MQTT broker transports the encrypted package rather than plaintext telemetry.

The gateway:

1. Receives the package.
2. Confirms the MQTT topic matches the device identity.
3. Verifies the ML-DSA signature.
4. Checks the sequence number.
5. Performs hybrid key recovery.
6. Decrypts and authenticates the telemetry.
7. Stores the security decision.

---

## Platform Architecture

```
                         +----------------------+
                         |      React UI        |
                         |  Security Dashboard  |
                         +----------+-----------+
                                    |
                                    | REST
                                    v
                         +----------------------+
                         |       FastAPI        |
                         |       Backend        |
                         +----------+-----------+
                                    |
              +---------------------+---------------------+
              |                     |                     |
              v                     v                     v
      +---------------+     +---------------+     +---------------+
      | Crypto Layer  |     | MQTT Gateway  |     |  PostgreSQL   |
      +---------------+     +-------+-------+     +---------------+
                                    |
                                    v
                            +---------------+
                            |   Mosquitto   |
                            +-------+-------+
                                    |
                    +---------------+---------------+
                    |               |               |
                    v               v               v
                 Sensor          Vehicle        Industrial
                 Device          Device           Device
```

---

## Technology Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Lucide React
- Recharts

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Paho MQTT

### Cryptography

- cryptography
- pqcrypto
- X25519
- ML-KEM-768
- ML-DSA-65
- HKDF-SHA384
- AES-256-GCM
- Ed25519 for classical benchmarking

### Infrastructure

- Docker
- Docker Compose
- Eclipse Mosquitto
- Nginx

### Testing

- Pytest
- Locust

---

## Project Structure

```
Hybrid-Post-Quantum-Cryptography/
|
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── benchmarks.py
│   │   │   ├── crypto.py
│   │   │   ├── devices.py
│   │   │   ├── health.py
│   │   │   ├── iot.py
│   │   │   ├── security.py
│   │   │   └── router.py
│   │   ├── crypto/
│   │   │   ├── hybrid.py
│   │   │   └── device_identity.py
│   │   ├── iot/
│   │   │   ├── mqtt_gateway.py
│   │   │   └── simulator.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── core/
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
|
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile
│   └── package.json
|
├── infrastructure/
│   └── mosquitto/
│       └── mosquitto.conf
|
├── loadtests/
│   └── locustfile.py
|
├── docs/
│   └── phase4-6.md
|
├── docker-compose.yml
├── pytest.ini
└── README.md
```

---

## Dashboard

The web application provides the following sections:

| Page | Purpose |
|---|---|
| Dashboard | Platform overview and health |
| Devices | Device registry and cryptographic provisioning |
| Encryption Lab | Interactive encryption/decryption |
| Live IoT | MQTT telemetry and verification |
| Handshake | Hybrid key-establishment visualization |
| Security Events | Persistent security decisions |
| Benchmarks | Classical/PQC/Hybrid performance |
| Audit Logs | Platform audit history |
| System | Infrastructure and cryptographic status |

---

## API

### Health

```http
GET /api/v1/health
```

### Devices

```http
GET  /api/v1/devices
POST /api/v1/devices
```

### Cryptography

```http
GET  /api/v1/crypto/info
POST /api/v1/crypto/encrypt
POST /api/v1/crypto/decrypt
```

### IoT

```http
GET  /api/v1/iot/status
POST /api/v1/iot/publish
GET  /api/v1/iot/messages
```

### Device Security

```http
POST /api/v1/security/devices/{device_id}/provision
GET  /api/v1/security/devices/{device_id}/crypto
POST /api/v1/security/gateway/provision
```

### Security Monitoring

```http
GET /api/v1/security/events
GET /api/v1/security/audit
```

### Benchmarks

```http
POST /api/v1/benchmarks/run
GET  /api/v1/benchmarks/history
```

Full interactive documentation is available through FastAPI Swagger UI.

---

## Benchmarking

PQShield evaluates three configurations.

### Classical

```
X25519 + AES-256-GCM + Ed25519
```

### Post-Quantum

```
ML-KEM-768 + AES-256-GCM + ML-DSA-65
```

### Hybrid

```
X25519 + ML-KEM-768
        +
HKDF-SHA384
        +
AES-256-GCM
        +
ML-DSA-65
```

The benchmark service records timing and package-size information in PostgreSQL and exposes the results through the dashboard.

---

## Load Testing

Start the default Docker load-test profile:

```bash
docker compose --profile loadtest up loadtest
```

Locust can be used to investigate:

- Throughput
- Request latency
- Cryptographic overhead
- Concurrent device behavior
- MQTT publishing
- Backend stability under load

The workload can be adjusted for different device/request counts.

---

## Installation and Setup

### Prerequisites

Recommended:

- Docker Desktop
- Git

For local development:

- Python 3.12+
- Node.js 22+
- npm

### Clone

```bash
git clone https://github.com/riagupta240619/Hybrid-Post-Quantum-Cryptography.git
cd Hybrid-Post-Quantum-Cryptography
```

### Run the complete platform

```bash
docker compose up --build
```

Services:

| Service | Address |
|---|---|
| Frontend | http://localhost:8080 |
| Backend | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| MQTT | localhost:1883 |
| PostgreSQL | localhost:5432 |

### Run the IoT simulator

In a second terminal:

```bash
docker compose --profile simulator up simulator
```

The simulator generates telemetry periodically and sends encrypted packages through MQTT.

---

## Testing

Run the backend test suite from the repository root:

```bash
python -m pytest backend/tests -q
```

The tests cover:

- Hybrid encryption/decryption
- Signature verification
- Tamper rejection
- Device identities
- MQTT gateway processing
- Replay protection
- Security event persistence
- Benchmark behavior

---

## Project Phases

### Phase 1 — Platform Foundation

- FastAPI backend
- PostgreSQL
- Device registry
- React frontend
- Docker infrastructure
- API foundation

### Phase 2 — Hybrid Cryptography

- X25519
- ML-KEM-768
- HKDF-SHA384
- AES-256-GCM
- ML-DSA-65
- Tamper detection
- Cryptographic tests

### Phase 3 — IoT Integration

- MQTT/Mosquitto
- Encrypted telemetry
- MQTT gateway
- Virtual IoT simulator
- Gateway-side verification

### Phase 4 — Security Platform

- Device cryptographic identities
- Security events
- Audit logs
- Gateway identity
- Replay protection
- Security dashboard

### Phase 5 — Benchmarking

- Classical benchmark
- PQC benchmark
- Hybrid benchmark
- Persistent benchmark history
- Benchmark dashboard

### Phase 6 — Scalability

- Locust load testing
- Docker load-test profile
- CI workflow
- Scalability experimentation

---

## Security Considerations

### Private Keys

The current research implementation keeps private cryptographic material in process memory.

No private key material is returned through public metadata APIs.

### MQTT

The included Mosquitto configuration is intended for local development. Production deployment should use:

- TLS
- Authentication
- Authorization
- MQTT ACLs
- Certificate management

### Replay State

Replay protection state is currently held in memory and resets when the gateway restarts.

### Key Management

The current implementation does not use a production KMS, HSM, or Vault deployment.

---

## Limitations

PQShield is a **research and educational prototype**, not a production-ready cryptographic protocol.

Important limitations include:

1. Private keys are currently process-memory based.
2. Replay state is currently in memory.
3. MQTT is configured for local development.
4. No external KMS/HSM/Vault is integrated.
5. The hybrid package format is project-specific.
6. Performance results depend on hardware, software versions, payload sizes, and workload.
7. Formal protocol verification has not been performed.

The hybrid X25519 + ML-KEM key combiner used by the project is a project-level construction and should not be interpreted as a standardized interoperable wire protocol.

---

## Future Scope

Potential extensions include:

- HashiCorp Vault integration
- Cloud KMS integration
- HSM-backed keys
- Persistent distributed replay protection
- Mutual TLS
- Device certificates
- Device revocation
- Automated key rotation
- Role-based access control
- Kubernetes deployment
- Redis-based asynchronous workers
- Distributed crypto workers
- Prometheus/Grafana monitoring
- Real IoT hardware
- Larger distributed load testing
- Formal protocol analysis
- Additional PQC algorithms

---

## Research Significance

PQShield demonstrates the intersection of:

```
Post-Quantum Cryptography
          +
IoT Security
          +
Applied Cryptography
          +
Security Engineering
          +
Performance Analysis
```

The project provides a practical environment for studying the migration from classical cryptography toward post-quantum cryptographic systems.

It can be used for:

- Academic demonstrations
- Cryptographic experimentation
- IoT security research
- Performance comparison
- PQC migration studies
- Security engineering projects

---

## Project Status

**Feature-complete research prototype**

The current platform includes:

```
Hybrid Cryptography
        ↓
IoT/MQTT Communication
        ↓
Device Cryptographic Identity
        ↓
Replay Protection
        ↓
Security Events
        ↓
Audit Logging
        ↓
Benchmarking
        ↓
Load Testing
        ↓
Web Security Dashboard
```

Production deployment would require additional key-management infrastructure, authentication, secure MQTT configuration, persistent replay state, protocol review, and operational hardening.

---

## Author

**Ria Gupta**

B.E. Computer Science and Engineering

Project domains:

- Cybersecurity
- Post-Quantum Cryptography
- IoT Security
- Applied Cryptography
- Security Engineering

---

## License

This project is intended for academic, research, and educational purposes.
