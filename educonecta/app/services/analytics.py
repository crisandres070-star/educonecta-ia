from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asistencia import Asistencia
from app.models.nota import Nota


def promedio_notas_alumno(db: Session, alumno_id: int) -> float | None:
    notas = db.scalars(select(Nota.valor).where(Nota.alumno_id == alumno_id)).all()
    if not notas:
        return None
    return round(mean(notas), 2)


def tasa_asistencia_alumno(db: Session, alumno_id: int) -> float | None:
    registros = db.scalars(select(Asistencia).where(Asistencia.alumno_id == alumno_id)).all()
    if not registros:
        return None
    presentes = sum(1 for r in registros if r.presente)
    return round((presentes / len(registros)) * 100, 2)
