from __future__ import annotations

import json
import logging
import threading
from collections import deque
from datetime import datetime, timezone
from typing import Any

import paho.mqtt.client as mqtt

from app.crypto.hybrid import CryptoPackageError, HybridCryptoService

logger = logging.getLogger(__name__)


class MqttGateway:
    """MQTT transport bridge that decrypts PQShield packages received from devices."""

    def __init__(
        self,
        crypto_service: HybridCryptoService,
        host: str,
        port: int,
        topic_prefix: str,
    ) -> None:
        self.crypto_service = crypto_service
        self.host = host
        self.port = port
        self.topic_prefix = topic_prefix.strip("/")
        self._messages: deque[dict[str, Any]] = deque(maxlen=100)
        self._lock = threading.Lock()
        self._connected = False
        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="pqshield-gateway",
        )
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

    @property
    def telemetry_topic(self) -> str:
        return f"{self.topic_prefix}/+/telemetry"

    @property
    def connected(self) -> bool:
        return self._connected

    def start(self) -> None:
        try:
            self._client.connect(self.host, self.port, keepalive=30)
            self._client.loop_start()
        except Exception:
            logger.exception("MQTT broker is unavailable at %s:%s", self.host, self.port)

    def stop(self) -> None:
        try:
            self._client.loop_stop()
            if self._connected:
                self._client.disconnect()
        finally:
            self._connected = False

    def publish(self, device_id: str, package: dict[str, Any]) -> None:
        if not self._connected:
            raise RuntimeError("MQTT gateway is not connected")
        topic = f"{self.topic_prefix}/{device_id}/telemetry"
        payload = json.dumps(package, sort_keys=True, separators=(",", ":"))
        result = self._client.publish(topic, payload=payload, qos=1)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"MQTT publish failed with code {result.rc}")

    def recent_messages(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._messages)

    def _on_connect(self, _client: mqtt.Client, _userdata: Any, _flags: Any, reason_code: Any, _properties: Any = None) -> None:
        if reason_code == 0:
            self._connected = True
            self._client.subscribe(self.telemetry_topic, qos=1)
            logger.info("Connected to MQTT broker and subscribed to %s", self.telemetry_topic)
        else:
            logger.error("MQTT connection failed: %s", reason_code)

    def _on_disconnect(self, _client: mqtt.Client, _userdata: Any, _disconnect_flags: Any, reason_code: Any, _properties: Any = None) -> None:
        self._connected = False
        logger.warning("MQTT gateway disconnected: %s", reason_code)

    def _on_message(self, _client: mqtt.Client, _userdata: Any, message: mqtt.MQTTMessage) -> None:
        received_at = datetime.now(timezone.utc).isoformat()
        try:
            package = json.loads(message.payload.decode("utf-8"))
            plaintext = self.crypto_service.decrypt(package)
            telemetry = json.loads(plaintext.decode("utf-8"))
            device_id = str(package["device_id"])
            event = {
                "device_id": device_id,
                "topic": message.topic,
                "received_at": received_at,
                "telemetry": telemetry,
                "security": {
                    "verified": True,
                    "pqc_kem": package["pqc_kem"],
                    "classical_kem": package["classical_kem"],
                    "signature": package["signature"],
                    "aead": package["aead"],
                },
            }
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError, CryptoPackageError) as error:
            logger.warning("Rejected MQTT package: %s", error)
            event = {
                "topic": message.topic,
                "received_at": received_at,
                "security": {"verified": False},
                "error": str(error),
            }

        with self._lock:
            self._messages.appendleft(event)
