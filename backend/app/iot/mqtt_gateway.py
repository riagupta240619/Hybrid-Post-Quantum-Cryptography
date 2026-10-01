from __future__ import annotations
import json, logging, threading
from collections import deque
from datetime import datetime, timezone
from typing import Any
import paho.mqtt.client as mqtt
from app.crypto.device_identity import DeviceCryptoError, DeviceCryptoRegistry, registry
from app.crypto.hybrid import CryptoPackageError, HybridCryptoService
from app.db.session import SessionLocal
from app.services.audit import security_event

logger=logging.getLogger(__name__)

class MqttGateway:
    def __init__(self, crypto_service:HybridCryptoService, host:str, port:int, topic_prefix:str, device_registry:DeviceCryptoRegistry|None=None)->None:
        self.crypto_service=crypto_service; self.device_registry=device_registry or registry; self.host=host; self.port=port; self.topic_prefix=topic_prefix.strip("/")
        self._messages:deque[dict[str,Any]]=deque(maxlen=100); self._highest_sequence:dict[str,int]={}; self._lock=threading.Lock(); self._connected=False
        self._client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id="pqshield-gateway"); self._client.on_connect=self._on_connect; self._client.on_disconnect=self._on_disconnect; self._client.on_message=self._on_message
    @property
    def telemetry_topic(self)->str:return f"{self.topic_prefix}/+/telemetry"
    @property
    def connected(self)->bool:return self._connected
    def start(self)->None:
        try:self._client.connect(self.host,self.port,keepalive=30); self._client.loop_start()
        except Exception:logger.exception("MQTT broker is unavailable at %s:%s",self.host,self.port)
    def stop(self)->None:
        try:
            self._client.loop_stop()
            if self._connected:self._client.disconnect()
        finally:self._connected=False
    def publish(self,device_id:str,package:dict[str,Any])->None:
        if not self._connected:raise RuntimeError("MQTT gateway is not connected")
        result=self._client.publish(f"{self.topic_prefix}/{device_id}/telemetry",payload=json.dumps(package,sort_keys=True,separators=(",",":")),qos=1)
        if result.rc!=mqtt.MQTT_ERR_SUCCESS:raise RuntimeError(f"MQTT publish failed with code {result.rc}")
    def recent_messages(self)->list[dict[str,Any]]:
        with self._lock:return list(self._messages)
    def _persist_event(self,event_type:str,result:str,verified:bool,device_id:str|None,sequence:int|None,details:dict[str,Any])->None:
        try:
            with SessionLocal() as session:security_event(session,event_type=event_type,result=result,verified=verified,device_id=device_id,sequence=sequence,details=details)
        except Exception:logger.exception("Could not persist security event")
    def _record_rejection(self,topic:str,received_at:str,error:str,device_id:str|None=None,sequence:int|None=None)->None:
        logger.warning("Rejected MQTT package: %s",error)
        with self._lock:self._messages.appendleft({"topic":topic,"received_at":received_at,"security":{"verified":False,"replay_protection":True},"error":error})
        self._persist_event("MESSAGE_REJECTED","blocked",False,device_id,sequence,{"topic":topic,"error":error})
    def _on_connect(self,_client: mqtt.Client,_userdata:Any,_flags:Any,reason_code:Any,_properties:Any=None)->None:
        if reason_code==0:self._connected=True; self._client.subscribe(self.telemetry_topic,qos=1); logger.info("Connected to MQTT broker and subscribed to %s",self.telemetry_topic)
        else:logger.error("MQTT connection failed: %s",reason_code)
    def _on_disconnect(self,_client: mqtt.Client,_userdata:Any,_disconnect_flags:Any,reason_code:Any,_properties:Any=None)->None:
        self._connected=False; logger.warning("MQTT gateway disconnected: %s",reason_code)
    def _on_message(self,_client: mqtt.Client,_userdata:Any,message: mqtt.MQTTMessage)->None:
        received_at=datetime.now(timezone.utc).isoformat(); device_id=None; sequence=None
        try:
            package=json.loads(message.payload.decode("utf-8")); device_id=str(package["device_id"]); parts=message.topic.strip("/").split("/")
            if len(parts)<3 or parts[-2]!=device_id or parts[-1]!="telemetry":raise CryptoPackageError("MQTT topic does not match package device_id")
            sequence=package.get("sequence")
            if not isinstance(sequence,int) or isinstance(sequence,bool) or sequence<0:raise CryptoPackageError("Missing or invalid replay-protection sequence")
            identity_aware="recipient_device_id" in package and package.get("version")==self.device_registry.VERSION
            plaintext=self.device_registry.decrypt_for("pqshield-gateway",package) if identity_aware else self.crypto_service.decrypt(package)
            telemetry=json.loads(plaintext.decode("utf-8"))
            with self._lock:
                highest=self._highest_sequence.get(device_id)
                if highest is not None and sequence<=highest:raise CryptoPackageError(f"Replay detected for {device_id}: sequence {sequence} is not newer than {highest}")
                self._highest_sequence[device_id]=sequence
            event={"device_id":device_id,"topic":message.topic,"received_at":received_at,"telemetry":telemetry,"security":{"verified":True,"replay_protection":True,"identity_aware":identity_aware,"sequence":sequence,"pqc_kem":package["pqc_kem"],"classical_kem":package["classical_kem"],"signature":package["signature"],"aead":package["aead"]}}
        except (UnicodeDecodeError,json.JSONDecodeError,KeyError,TypeError,ValueError,CryptoPackageError,DeviceCryptoError) as error:
            self._record_rejection(message.topic,received_at,str(error),device_id,sequence); return
        with self._lock:self._messages.appendleft(event)
        self._persist_event("MESSAGE_ACCEPTED","accepted",True,device_id,sequence,{"topic":message.topic,"identity_aware":event["security"]["identity_aware"]})
