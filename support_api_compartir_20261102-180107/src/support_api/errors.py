"""Excepciones de negocio convertidas a respuestas HTTP por la aplicacion."""

class ApiError(Exception):
    """Error base con el detalle y codigo HTTP que debe devolver la API."""

    status_code = 400

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class InvalidRequestIdError(ApiError):
    """El identificador no respeta el formato SOL-nnn."""

    status_code = 422


class UserNotFoundError(ApiError):
    """El usuario indicado no esta en el catalogo de apoyo."""

    status_code = 422


class RequestNotFoundError(ApiError):
    """No existe una solicitud con el identificador solicitado."""

    status_code = 404


class InvalidTransitionError(ApiError):
    """La transicion solicitada no pertenece al flujo permitido."""

    status_code = 409


class ClosedRequestError(ApiError):
    """Se intento modificar una solicitud que ya esta cerrada."""

    status_code = 409


class ResolutionNoteRequiredError(ApiError):
    """Falta una nota de resolucion valida para resolver o cerrar."""

    status_code = 422
