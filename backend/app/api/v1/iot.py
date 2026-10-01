import json
from fastapi import APIRouter, HTTPException, status
from app.api.v1.crypto import crypto_service
from app.core.config import get_settings
from app.crypto.device_identity import DeviceCryptoError, registry
from app.iot.mqtt_gateway import MqttGateway
from app.schemas.iot import IotMessage, IotPublishRequest, IotPublishResponse

router=APIRouter(prefix="/iot",tags=["iot"]); settings=get_settings()
mqtt_gateway=MqttGateway(crypto_service=crypto_service,host=settings.mqtt_host,port=settings.mqtt_port,topic_prefix=settings.mqtt_topic_prefix,device_registry=registry)
GATEWAY_ID="pqshield-gateway"

@router.get("/status")
def mqtt_status()->dict[str,object]:
    return {"enabled":settings.mqtt_enabled,"connected":mqtt_gateway.connected,"broker":f"{settings.mqtt_host}:{settings.mqtt_port}","telemetry_topic":mqtt_gateway.telemetry_topic,"replay_protection":True,"device_identity_mode":True}

@router.post("/publish",response_model=IotPublishResponse,status_code=status.HTTP_202_ACCEPTED)
def publish_telemetry(request:IotPublishRequest)->IotPublishResponse:
    if not mqtt_gateway.connected: raise HTTPException(status_code=503,detail="MQTT broker is unavailable")
    plaintext=json.dumps(request.telemetry,sort_keys=True,separators=(",",":")).encode("utf-8")
    identity_aware=registry.has_private_identity(request.device_id)
    try:
        package=registry.encrypt_for(request.device_id,GATEWAY_ID,plaintext,request.associated_data.encode("utf-8"),request.sequence) if identity_aware else crypto_service.encrypt(plaintext,request.associated_data.encode("utf-8"),request.device_id,request.sequence)
        mqtt_gateway.publish(request.device_id,package)
    except (DeviceCryptoError,RuntimeError) as error: raise HTTPException(status_code=503,detail=str(error)) from error
    return IotPublishResponse(device_id=request.device_id,topic=f"{settings.mqtt_topic_prefix}/{request.device_id}/telemetry",security={"classical_kem":package["classical_kem"],"pqc_kem":package["pqc_kem"],"aead":package["aead"],"signature":package["signature"],"identity_aware":str(identity_aware)},package=package)

@router.get("/messages",response_model=list[IotMessage])
def recent_messages()->list[IotMessage]: return [IotMessage(**event) for event in mqtt_gateway.recent_messages()]
