from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.alumno import Alumno


class TipoAlerta(StrEnum):
    DIFICULTAD_LECTORA = "dificultad_lectora"
    ATENCION = "atencion"
    CONDUCTA = "conducta"
    ACADEMICA = "academica"


class DetectadaPor(StrEnum):
    IA = "ia"
    PROFESOR = "profesor"


class AlertaAprendizaje(Base):
    __tablename__ = "alertas_aprendizaje"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alumno_id: Mapped[int] = mapped_column(ForeignKey("alumnos.id"), nullable=False, index=True)
    colegio_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    tipo: Mapped[TipoAlerta] = mapped_column(Enum(TipoAlerta, name="tipo_alerta"), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(600), nullable=False)
    detectada_por: Mapped[DetectadaPor] = mapped_column(Enum(DetectadaPor, name="detectada_por"), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    resuelta: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    alumno: Mapped["Alumno"] = relationship("Alumno", back_populates="alertas")
