from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Device
from app.schemas.device import DeviceCreate


class DuplicateDeviceError(Exception):
    pass


def list_devices(session: Session) -> list[Device]:
    statement = select(Device).order_by(Device.created_at.desc(), Device.id.desc())
    return list(session.scalars(statement).all())


def get_device(session: Session, device_id: str) -> Device | None:
    statement = select(Device).where(Device.device_id == device_id)
    return session.scalar(statement)


def create_device(session: Session, device_data: DeviceCreate) -> Device:
    device = Device(**device_data.model_dump())
    session.add(device)

    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DuplicateDeviceError(device_data.device_id) from error

    session.refresh(device)
    return device