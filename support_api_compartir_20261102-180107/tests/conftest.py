"""Fixtures reutilizables para ejecutar pruebas aisladas de la API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from support_api.database import Base, get_db
from support_api.main import create_app
from support_api.models import SupportUser


@pytest.fixture
def client() -> TestClient:
    """Crea un cliente conectado a SQLite en memoria y elimina los datos al final."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        for user_id in ("USR-01", "USR-02", "USR-03"):
            session.add(SupportUser(id=user_id))
        session.commit()

    def override_get_db():
        with TestingSessionLocal() as session:
            yield session

    app = create_app(initialize_storage=False)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def create_payload() -> dict[str, str]:
    """Devuelve una solicitud valida que las pruebas pueden reutilizar."""
    return {
        "id_usuario": "USR-01",
        "categoria": "HARDWARE",
        "descripcion": "El monitor secundario no enciende",
        "prioridad": "MEDIA",
    }
