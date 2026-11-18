"""Punto de entrada: configura FastAPI, almacenamiento y manejo de errores."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from support_api.database import init_database
from support_api.errors import ApiError
from support_api.routes import router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Prepara las tablas y los usuarios de apoyo al iniciar la API."""
    init_database()
    yield


def create_app(initialize_storage: bool = True) -> FastAPI:
    """Construye la aplicacion; permite desactivar el inicio de DB en pruebas."""
    app_lifespan = lifespan if initialize_storage else None
    application = FastAPI(
        title="API de Solicitudes de Soporte",
        version="0.1.0",
        description="Gestion del ciclo de vida de solicitudes de soporte tecnico.",
        lifespan=app_lifespan,
    )
    application.include_router(router)

    @application.exception_handler(ApiError)
    async def handle_api_error(_: Request, error: ApiError) -> JSONResponse:
        """Convierte errores del negocio en respuestas HTTP con detalle."""
        return JSONResponse(
            status_code=error.status_code,
            content={"detail": error.detail},
        )

    @application.get("/health", tags=["salud"])
    def health_check() -> dict[str, str]:
        """Confirma que el proceso de la API esta respondiendo."""
        return {"status": "ok"}

    return application


app = create_app()
