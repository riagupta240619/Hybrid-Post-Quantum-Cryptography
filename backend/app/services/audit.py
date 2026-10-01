import json
from sqlalchemy.orm import Session
from app.models import AuditLog, SecurityEvent

def audit(session: Session, action: str, actor: str = "system", device_id: str | None = None, details: dict | None = None) -> None:
    session.add(AuditLog(action=action, actor=actor, device_id=device_id, details=json.dumps(details or {}, sort_keys=True)))
    session.commit()

def security_event(session: Session, event_type: str, result: str, verified: bool, device_id: str | None = None, sequence: int | None = None, details: dict | None = None) -> None:
    session.add(SecurityEvent(event_type=event_type, result=result, verified=verified, device_id=device_id, sequence=sequence, details=json.dumps(details or {}, sort_keys=True)))
    session.commit()
