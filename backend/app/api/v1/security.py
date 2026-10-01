import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.crypto.device_identity import DeviceCryptoError, registry
from app.db.session import get_db_session
from app.models import AuditLog, Device, DeviceCryptoIdentity, SecurityEvent
from app.schemas.security import AuditLogRead, CryptoIdentityRead, SecurityEventRead
from app.services.audit import audit

router = APIRouter(prefix="/security", tags=["security"])
GATEWAY_ID = "pqshield-gateway"

@router.post("/devices/{device_id}/provision", response_model=CryptoIdentityRead, status_code=status.HTTP_201_CREATED)
def provision_device(device_id: str, session: Session = Depends(get_db_session)) -> CryptoIdentityRead:
    device = session.scalar(select(Device).where(Device.device_id == device_id))
    if device is None:
        raise HTTPException(status_code=404, detail="Device is not registered")
    meta = registry.provision(device_id)
    existing = session.scalar(select(DeviceCryptoIdentity).where(DeviceCryptoIdentity.device_id == device_id))
    if existing is None:
        existing = DeviceCryptoIdentity(device_id=device_id, x25519_public_key=meta["x25519_public_key"], mlkem_public_key=meta["mlkem_public_key"], mldsa_public_key=meta["mldsa_public_key"])
        session.add(existing)
    else:
        existing.x25519_public_key = meta["x25519_public_key"]
        existing.mlkem_public_key = meta["mlkem_public_key"]
        existing.mldsa_public_key = meta["mldsa_public_key"]
    session.commit()
    audit(session, "DEVICE_PROVISIONED", device_id=device_id, details={"version": meta["version"]})
    return CryptoIdentityRead(**meta)

@router.get("/devices/{device_id}/crypto", response_model=CryptoIdentityRead)
def device_crypto(device_id: str, session: Session = Depends(get_db_session)) -> CryptoIdentityRead:
    row = session.scalar(select(DeviceCryptoIdentity).where(DeviceCryptoIdentity.device_id == device_id))
    if row is None or not registry.has_private_identity(device_id):
        raise HTTPException(status_code=404, detail="No active in-memory identity; provision the device")
    return CryptoIdentityRead(**registry.public_metadata(device_id))

@router.post("/gateway/provision", response_model=CryptoIdentityRead)
def provision_gateway(session: Session = Depends(get_db_session)) -> CryptoIdentityRead:
    meta = registry.ensure(GATEWAY_ID)
    existing = session.scalar(select(DeviceCryptoIdentity).where(DeviceCryptoIdentity.device_id == GATEWAY_ID))
    if existing is None:
        session.add(DeviceCryptoIdentity(device_id=GATEWAY_ID, x25519_public_key=meta["x25519_public_key"], mlkem_public_key=meta["mlkem_public_key"], mldsa_public_key=meta["mldsa_public_key"]))
        session.commit()
    return CryptoIdentityRead(**meta)

@router.get("/events", response_model=list[SecurityEventRead])
def security_events(limit: int = 100, session: Session = Depends(get_db_session)) -> list[SecurityEventRead]:
    rows = session.scalars(select(SecurityEvent).order_by(SecurityEvent.created_at.desc()).limit(max(1, min(limit, 500)))).all()
    return [SecurityEventRead(id=r.id, device_id=r.device_id, event_type=r.event_type, result=r.result, verified=r.verified, sequence=r.sequence, details=json.loads(r.details or "{}"), created_at=r.created_at) for r in rows]

@router.get("/audit", response_model=list[AuditLogRead])
def audit_logs(limit: int = 100, session: Session = Depends(get_db_session)) -> list[AuditLogRead]:
    rows = session.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(max(1, min(limit, 500)))).all()
    return [AuditLogRead(id=r.id, action=r.action, actor=r.actor, device_id=r.device_id, details=json.loads(r.details or "{}"), created_at=r.created_at) for r in rows]
