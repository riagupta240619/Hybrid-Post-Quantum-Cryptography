from __future__ import annotations

import json
import os
import random
import time
import urllib.request

import paho.mqtt.client as mqtt

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "pqshield").strip("/")
DEVICE_ID = os.getenv("DEVICE_ID", "temperature-sensor-001")
INTERVAL = float(os.getenv("SIMULATOR_INTERVAL", "5"))


def request_encrypted_package(telemetry: dict[str, object], sequence: int) -> dict[str, object]:
    body = json.dumps(
        {
            "plaintext": json.dumps(telemetry, sort_keys=True, separators=(",", ":")),
            "device_id": DEVICE_ID,
            "associated_data": DEVICE_ID,
            "sequence": sequence,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{BACKEND_URL}/api/v1/crypto/encrypt",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))["package"]


def main() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"simulator-{DEVICE_ID}")
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
    client.loop_start()
    topic = f"{TOPIC_PREFIX}/{DEVICE_ID}/telemetry"
    sequence = 0

    try:
        while True:
            sequence += 1
            telemetry = {
                "temperature_c": round(random.uniform(20.0, 30.0), 2),
                "humidity_percent": round(random.uniform(35.0, 65.0), 2),
                "battery_percent": random.randint(65, 100),
                "sequence": sequence,
            }
            package = request_encrypted_package(telemetry, sequence)
            payload = json.dumps(package, sort_keys=True, separators=(",", ":"))
            result = client.publish(topic, payload=payload, qos=1)
            result.wait_for_publish()
            print(f"published encrypted telemetry for {DEVICE_ID}: {telemetry}", flush=True)
            time.sleep(INTERVAL)
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
