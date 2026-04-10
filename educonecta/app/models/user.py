from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(StrEnum):
    PROFESOR = "profesor"
    APODERADO = "apoderado"
    DIRECTIVO = "directivo"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    colegio_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    alumnos_apoderado: Mapped[list["Alumno"]] = relationship(
        "Alumno",
        back_populates="apoderado",
        foreign_keys="Alumno.apoderado_id",
    )
    notas_profesor: Mapped[list["Nota"]] = relationship("Nota", back_populates="profesor")
    anotaciones_profesor: Mapped[list["Anotacion"]] = relationship("Anotacion", back_populates="profesor")
