from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Alumno(Base):
    __tablename__ = "alumnos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    apellido: Mapped[str] = mapped_column(String(120), nullable=False)
    curso: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    colegio_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    apoderado_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    apoderado: Mapped["User"] = relationship("User", back_populates="alumnos_apoderado", foreign_keys=[apoderado_id])
    notas: Mapped[list["Nota"]] = relationship("Nota", back_populates="alumno", cascade="all, delete-orphan")
    anotaciones: Mapped[list["Anotacion"]] = relationship(
        "Anotacion", back_populates="alumno", cascade="all, delete-orphan"
    )
    asistencias: Mapped[list["Asistencia"]] = relationship(
        "Asistencia", back_populates="alumno", cascade="all, delete-orphan"
    )
    alertas: Mapped[list["AlertaAprendizaje"]] = relationship(
        "AlertaAprendizaje", back_populates="alumno", cascade="all, delete-orphan"
    )
