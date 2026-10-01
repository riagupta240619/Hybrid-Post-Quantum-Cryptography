from fastapi import APIRouter, HTTPException, status

from app.crypto.hybrid import CryptoPackageError, HybridCryptoService
from app.schemas.crypto import DecryptRequest, DecryptResponse, EncryptRequest, EncryptResponse

router = APIRouter(prefix="/crypto", tags=["crypto"])
crypto_service = HybridCryptoService()


@router.get("/info")
def crypto_info() -> dict[str, object]:
    return crypto_service.public_metadata()


@router.post("/encrypt", response_model=EncryptResponse)
def encrypt(request: EncryptRequest) -> EncryptResponse:
    package = crypto_service.encrypt(
        request.plaintext.encode("utf-8"),
        request.associated_data.encode("utf-8"),
        request.device_id,
    )
    return EncryptResponse(package=package)


@router.post("/decrypt", response_model=DecryptResponse)
def decrypt(request: DecryptRequest) -> DecryptResponse:
    try:
        plaintext = crypto_service.decrypt(request.package)
    except (CryptoPackageError, ValueError, TypeError) as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return DecryptResponse(plaintext=plaintext.decode("utf-8"))
