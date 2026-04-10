from datetime import date

from sqlalchemy import CheckConstraint, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Nota(Base):
    __tablename__ = "notas"
    __table_args__ = (CheckConstraint("valor >= 1.0 AND valor <= 7.0", name="check_nota_valor"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alumno_id: Mapped[int] = mapped_column(ForeignKey("alumnos.id"), nullable=False, index=True)
    colegio_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    asignatura: Mapped[str] = mapped_column(String(120), nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    profesor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(500), nullable=True)

    alumno: Mapped["Alumno"] = relationship("Alumno", back_populates="notas")
    profesor: Mapped["User"] = relationship("User", back_populates="notas_profesor")
