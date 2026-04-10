from datetime import date
from enum import StrEnum

from sqlalchemy import Date, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TipoAnotacion(StrEnum):
    POSITIVA = "positiva"
    NEGATIVA = "negativa"
    NEUTRA = "neutra"


class Anotacion(Base):
    __tablename__ = "anotaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alumno_id: Mapped[int] = mapped_column(ForeignKey("alumnos.id"), nullable=False, index=True)
    colegio_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    tipo: Mapped[TipoAnotacion] = mapped_column(Enum(TipoAnotacion, name="tipo_anotacion"), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    profesor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)

    alumno: Mapped["Alumno"] = relationship("Alumno", back_populates="anotaciones")
    profesor: Mapped["User"] = relationship("User", back_populates="anotaciones_profesor")
