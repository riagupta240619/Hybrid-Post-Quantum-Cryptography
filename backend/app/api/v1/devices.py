from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.device import DeviceCreate, DeviceRead
from app.services.devices import DuplicateDeviceError, create_device, get_device, list_devices

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=list[DeviceRead])
def read_devices(session: Session = Depends(get_db_session)) -> list[DeviceRead]:
    return list_devices(session)


@router.post("", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
def add_device(device_data: DeviceCreate, session: Session = Depends(get_db_session)) -> DeviceRead:
    try:
        return create_device(session, device_data)
    except DuplicateDeviceError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Device ID '{device_data.device_id}' already exists",
        ) from error


@router.get("/{device_id}", response_model=DeviceRead)
def read_device(device_id: str, session: Session = Depends(get_db_session)) -> DeviceRead:
    device = get_device(session, device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device