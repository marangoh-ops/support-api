"""Enumera valores permitidos y valida los datos de entrada y salida."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator


class Category(StrEnum):
    """Categorias de soporte aceptadas por el negocio."""

    HARDWARE = "HARDWARE"
    SOFTWARE = "SOFTWARE"
    REDES = "REDES"
    ACCESO = "ACCESO"


class Priority(StrEnum):
    """Niveles de prioridad permitidos."""

    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


class RequestStatus(StrEnum):
    """Estados disponibles en el ciclo de vida de una solicitud."""

    NUEVA = "NUEVA"
    EN_PROCESO = "EN_PROCESO"
    RESUELTA = "RESUELTA"
    CERRADA = "CERRADA"


class SupportRequestCreate(BaseModel):
    """Campos que el cliente debe enviar para registrar una solicitud."""

    id_usuario: str
    categoria: Category
    descripcion: str
    prioridad: Priority

    @field_validator("id_usuario")
    @classmethod
    def validate_user_id(cls, value: str) -> str:
        """Elimina espacios externos y rechaza identificadores vacios."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("id_usuario no puede estar vacio")
        return normalized

    @field_validator("descripcion")
    @classmethod
    def validate_description(cls, value: str) -> str:
        """Exige una descripcion de 10 a 500 caracteres."""
        normalized = value.strip()
        if not 10 <= len(normalized) <= 500:
            raise ValueError("descripcion debe contener entre 10 y 500 caracteres")
        return normalized


class StatusUpdate(BaseModel):
    """Datos para solicitar un cambio de estado y su nota opcional."""

    nuevo_estado: RequestStatus
    nota_resolucion: str | None = None

    @field_validator("nota_resolucion")
    @classmethod
    def validate_resolution_note(cls, value: str | None) -> str | None:
        """Normaliza la nota y rechaza las notas presentes con menos de 10 caracteres."""
        if value is None:
            return None
        normalized = value.strip()
        if len(normalized) < 10:
            raise ValueError("nota_resolucion debe contener al menos 10 caracteres")
        return normalized


class SupportRequestResponse(BaseModel):
    """Forma publica de una solicitud devuelta por la API."""

    model_config = ConfigDict(from_attributes=True)

    id_solicitud: str
    id_usuario: str
    categoria: Category
    descripcion: str
    prioridad: Priority
    estado: RequestStatus
    nota_resolucion: str | None
