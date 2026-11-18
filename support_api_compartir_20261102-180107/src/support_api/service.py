"""Reglas de negocio para crear, consultar y actualizar solicitudes."""

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from support_api.errors import (
    ClosedRequestError,
    InvalidRequestIdError,
    InvalidTransitionError,
    RequestNotFoundError,
    ResolutionNoteRequiredError,
    UserNotFoundError,
)
from support_api.models import SupportRequest, SupportUser
from support_api.schemas import (
    RequestStatus,
    StatusUpdate,
    SupportRequestCreate,
    SupportRequestResponse,
)


_ALLOWED_TRANSITIONS = {
    RequestStatus.NUEVA: {RequestStatus.EN_PROCESO, RequestStatus.CERRADA},
    RequestStatus.EN_PROCESO: {RequestStatus.RESUELTA},
    RequestStatus.RESUELTA: {RequestStatus.CERRADA},
    RequestStatus.CERRADA: set(),
}
_REQUEST_ID_PATTERN = re.compile(r"^SOL-(\d+)$")


def _request_id_to_integer(request_id: str) -> int:
    """Valida SOL-nnn y convierte el identificador publico a clave interna."""
    match = _REQUEST_ID_PATTERN.fullmatch(request_id.strip())
    if match is None or int(match.group(1)) < 1:
        raise InvalidRequestIdError("Formato de id_solicitud invalido")
    return int(match.group(1))


def _to_response(request: SupportRequest) -> SupportRequestResponse:
    """Adapta el modelo SQLAlchemy al esquema publico de respuesta."""
    return SupportRequestResponse(
        id_solicitud=f"SOL-{request.id:03d}",
        id_usuario=request.id_usuario,
        categoria=request.categoria,
        descripcion=request.descripcion,
        prioridad=request.prioridad,
        estado=request.estado,
        nota_resolucion=request.nota_resolucion,
    )


def create_request(
    session: Session, data: SupportRequestCreate
) -> SupportRequestResponse:
    """Verifica el usuario, crea la solicitud en NUEVA y confirma el cambio."""
    if session.get(SupportUser, data.id_usuario) is None:
        raise UserNotFoundError(f"El usuario {data.id_usuario} no existe")

    request = SupportRequest(
        id_usuario=data.id_usuario,
        categoria=data.categoria.value,
        descripcion=data.descripcion,
        prioridad=data.prioridad.value,
        estado=RequestStatus.NUEVA.value,
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    return _to_response(request)


def get_request(session: Session, request_id: str) -> SupportRequestResponse:
    """Obtiene una solicitud existente o genera un error de no encontrado."""
    internal_id = _request_id_to_integer(request_id)
    request = session.get(SupportRequest, internal_id)
    if request is None:
        raise RequestNotFoundError(f"La solicitud {request_id} no fue encontrada")
    return _to_response(request)


def list_requests(
    session: Session, status: RequestStatus
) -> list[SupportRequestResponse]:
    """Lista solicitudes de un estado en orden de creacion."""
    requests = session.scalars(
        select(SupportRequest)
        .where(SupportRequest.estado == status.value)
        .order_by(SupportRequest.id)
    ).all()
    return [_to_response(request) for request in requests]


def change_request_status(
    session: Session, request_id: str, data: StatusUpdate
) -> SupportRequestResponse:
    """Valida la transicion y la nota antes de cambiar y guardar el estado."""
    internal_id = _request_id_to_integer(request_id)
    request = session.get(SupportRequest, internal_id)
    if request is None:
        raise RequestNotFoundError(f"La solicitud {request_id} no fue encontrada")

    current_status = RequestStatus(request.estado)
    target_status = data.nuevo_estado
    if current_status is RequestStatus.CERRADA:
        raise ClosedRequestError("Una solicitud cerrada no permite modificaciones")
    if target_status not in _ALLOWED_TRANSITIONS[current_status]:
        raise InvalidTransitionError(
            f"Transicion no permitida de {current_status.value} a {target_status.value}"
        )
    if target_status in {RequestStatus.RESUELTA, RequestStatus.CERRADA}:
        if data.nota_resolucion is None or len(data.nota_resolucion.strip()) < 10:
            raise ResolutionNoteRequiredError(
                "Se requiere nota_resolucion de al menos 10 caracteres"
            )

    request.estado = target_status.value
    if data.nota_resolucion is not None:
        request.nota_resolucion = data.nota_resolucion
    session.commit()
    session.refresh(request)
    return _to_response(request)
