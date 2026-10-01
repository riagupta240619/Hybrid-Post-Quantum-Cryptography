# PQShield

**Hybrid Post-Quantum Security Platform**

PQShield is an academic software platform demonstrating a hybrid security layer for IoT and cloud environments.

## Current implementation

### Phase 2 — Hybrid cryptography
- X25519 + ML-KEM-768 hybrid key establishment
- HKDF-SHA384 key combination
- AES-256-GCM payload encryption
- ML-DSA-65 package authentication
- Tamper detection before decryption
- In-memory cryptographic identities for the research prototype

### Phase 3 — IoT/MQTT integration
- Eclipse Mosquitto MQTT broker in Docker Compose
- Secure telemetry topic convention: `pqshield/<device_id>/telemetry`
- FastAPI MQTT gateway
- Hybrid-encrypted telemetry packages transported over MQTT
- Gateway-side ML-DSA verification and AES-GCM decryption
- Recent decrypted telemetry view through the API
- Repeatable virtual temperature-sensor simulator
- Simulator runs through the optional Docker Compose `simulator` profile

The Phase 3 simulator intentionally uses the existing crypto API to obtain a signed hybrid package and then sends that package over MQTT. This keeps the demonstration reproducible while making the transport and gateway flow explicit. A later phase can introduce independent per-device cryptographic identities and key provisioning.

## Architecture

```text
Virtual IoT Device
      |
      | request hybrid package
      v
PQShield Crypto API
      |
      | X25519 + ML-KEM-768
      | HKDF-SHA384
      | AES-256-GCM
      | ML-DSA-65
      v
Encrypted Package
      |
      | MQTT QoS 1
      v
Mosquitto Broker
      |
      v
PQShield MQTT Gateway
      |
      | verify signature
      | derive key
      | decrypt telemetry
      v
Telemetry API
```

## Technology stack

- Frontend: React, TypeScript, Vite, Tailwind CSS
- Backend: Python, FastAPI, SQLAlchemy
- Cryptography: cryptography + pqcrypto
- Messaging: Eclipse Mosquitto + Paho MQTT
- Database: PostgreSQL
- Infrastructure: Docker Compose
- Tests: Pytest

## Run with Docker Compose

Start the platform:

```bash
docker compose up --build
```

Frontend: http://localhost:8080  
Backend: http://localhost:8000  
Swagger UI: http://localhost:8000/docs  
MQTT broker: localhost:1883

Run the virtual IoT simulator in a second command:

```bash
docker compose --profile simulator up simulator
```

The simulator publishes temperature, humidity, battery, and sequence telemetry every five seconds by default.

## Phase 3 API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v1/iot/status` | MQTT broker/gateway status |
| POST | `/api/v1/iot/publish` | Encrypt telemetry and publish it to MQTT |
| GET | `/api/v1/iot/messages` | View recently received/decrypted telemetry |

Example:

```json
{
  "device_id": "temperature-sensor-001",
  "telemetry": {
    "temperature_c": 24.5,
    "humidity_percent": 52.1,
    "battery_percent": 91
  },
  "associated_data": "temperature-sensor-001"
}
```

The broker payload contains the encrypted package, not plaintext telemetry.

## Tests

From the repository root:

```bash
python -m pytest backend/tests -q
```

## Security scope

This is a research/demo platform, not a production protocol implementation. Private cryptographic keys remain in memory in the current phase. The MQTT broker is intentionally configured without authentication for local development; production deployment should use TLS, broker authentication/authorization, device identities, and external key management.
