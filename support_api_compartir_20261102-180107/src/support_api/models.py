"""Modelos ORM que representan las tablas persistidas en SQLite."""

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from support_api.database import Base


class SupportUser(Base):
    """Catalogo minimo de usuarios habilitados para crear solicitudes."""

    __tablename__ = "support_users"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)


class SupportRequest(Base):
    """Registro persistido de una solicitud y su estado actual."""

    __tablename__ = "support_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[str] = mapped_column(
        String(32), ForeignKey("support_users.id"), nullable=False, index=True
    )
    categoria: Mapped[str] = mapped_column(String(20), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    prioridad: Mapped[str] = mapped_column(String(20), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    nota_resolucion: Mapped[str | None] = mapped_column(Text, nullable=True)
