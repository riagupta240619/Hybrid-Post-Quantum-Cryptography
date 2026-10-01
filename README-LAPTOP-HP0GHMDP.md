# PQShield

**Hybrid Post-Quantum Security Platform**

PQShield is an academic software platform exploring a hybrid post-quantum security layer for IoT and cloud environments. The repository now contains the Phase 1 service foundation plus the first real cryptographic implementation in Phase 2.

> Phase 2 is an academic/research implementation. It uses established cryptographic libraries rather than implementing primitives from scratch. Private keys are kept in memory only; no production key-management system is claimed.

## Phase 2 Cryptographic Design

PQShield uses a true hybrid public-key key-establishment construction:

```text
Plaintext
   |
AES-256-GCM <--- HKDF-SHA384 <--- X25519 shared secret
   |                         ^
   |                         |
Encrypted package            +--- ML-KEM-768 shared secret
   |
ML-DSA-65 signature
   |
Signed encrypted package
```

### Algorithms

| Component | Algorithm | Purpose |
| --- | --- | --- |
| Classical key establishment | X25519 | Provides the classical shared secret |
| Post-quantum KEM | ML-KEM-768 | Provides a post-quantum shared secret |
| Key combiner | HKDF-SHA384 | Combines both shared secrets into a 256-bit AES key |
| Payload encryption | AES-256-GCM | Confidentiality and authenticated encryption |
| Digital signature | ML-DSA-65 | Authenticates the canonical encrypted package |

The hybrid combiner is the project-level construction:
`HKDF-SHA384(X25519_shared_secret || ML-KEM_shared_secret)`
This is documented explicitly and is not presented as a standardized wire protocol.

## Phase 2 API

| Method | Endpoint | Behavior |
| --- | --- | --- |
| GET | /api/v1/crypto/info | Public algorithm and public-key metadata |
| POST | /api/v1/crypto/encrypt | Hybrid-encrypt UTF-8 plaintext and return a signed package |
| POST | /api/v1/crypto/decrypt | Verify, decapsulate, derive the AES key, and decrypt a package |

Example encryption request:

```json
{
  "plaintext": "temperature=24.5C",
  "device_id": "sensor-001",
  "associated_data": "sensor=v1"
}
```

The response contains the encrypted package, including algorithm identifiers, an ephemeral X25519 public key, ML-KEM ciphertext, nonce, AES-GCM ciphertext, associated data, and ML-DSA signature. Private keys are never returned by the API.

## Phase 1 Scope

- FastAPI application with environment configuration, CORS, SQLAlchemy, and /api/v1 routes.
- PostgreSQL-backed device creation, listing, and retrieval.
- React, TypeScript, Vite, and Tailwind application shell with working device management.
- Docker Compose development environment for PostgreSQL, backend, and frontend.
- Pytest backend tests using an isolated in-memory SQLite database.

## Technology Stack

- Frontend: React, TypeScript, Vite, Tailwind CSS
- Backend: Python 3.12, FastAPI, Pydantic, SQLAlchemy
- Cryptography: cryptography, pqcrypto
- Database: PostgreSQL
- Infrastructure: Docker, Docker Compose
- Tests: Pytest, FastAPI TestClient, isolated SQLite

## Requirements

- Docker Engine/Desktop with the Compose plugin for containerized use.
- For local development: Python 3.11+, Node.js 20+, npm, and a PostgreSQL instance.

## Docker Compose

From the repository root:

```bash
docker compose up --build
```

Open the frontend at http://localhost:8080. The backend is available at http://localhost:8000 and its interactive API documentation is at http://localhost:8000/docs.

## Local Development

Backend:

```bash
python -m venv .venv
python -m pip install -r backend/requirements.txt
python -m pytest backend/tests -q
python -m uvicorn app.main:app --app-dir backend --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Phase 2 Testing

The Phase 2 tests cover:

- successful hybrid encrypt/decrypt round trip;
- presence of X25519, ML-KEM-768, AES-256-GCM, and ML-DSA-65 in the package;
- rejection of modified ciphertext through ML-DSA authentication;
- rejection of packages created under a different in-memory key identity;
- prevention of private-key exposure through the public metadata endpoint.

## Roadmap

1. Phase 1: service foundation and PostgreSQL-backed device registry. Complete.
2. Phase 2: real cryptographic provider boundary and hybrid encrypt/decrypt API. Current branch.
3. Phase 3: device simulation and MQTT transport.
4. Phase 4: platform features, audit events, key-management abstraction, and dashboard integration.
5. Phase 5: classical vs PQC vs hybrid benchmarks and research reporting.
6. Phase 6: scalable workers and load testing.

The Phase 2 in-memory key lifecycle is not production key management. A later phase should introduce a KMS/Vault/HSM abstraction before persistent deployment.
