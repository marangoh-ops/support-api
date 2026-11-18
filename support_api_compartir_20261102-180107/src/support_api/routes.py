"""Declara las rutas HTTP y conecta cada una con el servicio de negocio."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from support_api.database import get_db
from support_api.schemas import (
    RequestStatus,
    StatusUpdate,
    SupportRequestCreate,
    SupportRequestResponse,
)
from support_api.service import (
    change_request_status,
    create_request,
    get_request,
    list_requests,
)


router = APIRouter(prefix="/api/v1/solicitudes", tags=["solicitudes"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=SupportRequestResponse, status_code=201)
def create_support_request(
    data: SupportRequestCreate, session: DatabaseSession
) -> SupportRequestResponse:
    """Crea una solicitud validada y responde con estado HTTP 201."""
    return create_request(session, data)


@router.get("", response_model=list[SupportRequestResponse])
def get_support_requests(
    session: DatabaseSession,
    estado: Annotated[RequestStatus, Query(description="Estado por el que filtrar")],
) -> list[SupportRequestResponse]:
    """Devuelve las solicitudes cuyo estado coincide con el filtro."""
    return list_requests(session, estado)


@router.get("/consulta", response_model=SupportRequestResponse)
def get_support_request_by_query(
    id_solicitud: Annotated[
        str, Query(description="Identificador de la solicitud, por ejemplo SOL-001")
    ],
    session: DatabaseSession,
) -> SupportRequestResponse:
    """Consulta por ID recibido como parametro para validar valores vacios."""
    return get_request(session, id_solicitud)


@router.get("/{id_solicitud}", response_model=SupportRequestResponse)
def get_support_request(
    id_solicitud: str, session: DatabaseSession
) -> SupportRequestResponse:
    """Busca y devuelve una solicitud por su identificador publico."""
    return get_request(session, id_solicitud)


@router.patch("/{id_solicitud}/estado", response_model=SupportRequestResponse)
def patch_support_request_status(
    id_solicitud: str, data: StatusUpdate, session: DatabaseSession
) -> SupportRequestResponse:
    """Solicita al servicio una transicion de estado para una solicitud."""
    return change_request_status(session, id_solicitud, data)
