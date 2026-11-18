"""Configura SQLAlchemy, sesiones y datos iniciales de SQLite."""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.getenv("SUPPORT_DATABASE_URL", "sqlite:///./support_requests.db")
_engine_options = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_engine_options)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Clase base de la que heredan los modelos de persistencia."""

    pass


def get_db() -> Generator[Session, None, None]:
    """Entrega una sesion por peticion y la cierra al finalizar."""
    with SessionLocal() as session:
        yield session


def init_database() -> None:
    """Crea tablas y agrega usuarios ficticios si aun no existen."""
    from support_api.models import SupportUser

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        for user_id in ("USR-01", "USR-02", "USR-03"):
            if session.get(SupportUser, user_id) is None:
                session.add(SupportUser(id=user_id))
        session.commit()
