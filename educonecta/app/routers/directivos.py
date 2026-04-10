from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import require_roles
from app.models.alerta_aprendizaje import AlertaAprendizaje
from app.models.alumno import Alumno
from app.models.asistencia import Asistencia
from app.models.nota import Nota
from app.models.user import User, UserRole
from app.schemas.alerta import AlertaRead
from app.schemas.directivo import DashboardRead, RendimientoCursoRead

router = APIRouter(prefix="/directivo", tags=["Directivos"])


@router.get("/dashboard", response_model=DashboardRead)
def dashboard_colegio(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.DIRECTIVO)),
) -> DashboardRead:
    total_alumnos = db.scalar(select(func.count(Alumno.id)).where(Alumno.colegio_id == current_user.colegio_id)) or 0
    promedio_general = db.scalar(
        select(func.avg(Nota.valor))
        .join(Alumno, Nota.alumno_id == Alumno.id)
        .where(Alumno.colegio_id == current_user.colegio_id)
    )
    alertas_activas = db.scalar(
        select(func.count(AlertaAprendizaje.id))
        .join(Alumno, AlertaAprendizaje.alumno_id == Alumno.id)
        .where(Alumno.colegio_id == current_user.colegio_id, AlertaAprendizaje.resuelta.is_(False))
    ) or 0

    inasistencias = db.scalar(
        select(func.count(Asistencia.id))
        .join(Alumno, Asistencia.alumno_id == Alumno.id)
        .where(Alumno.colegio_id == current_user.colegio_id, Asistencia.presente.is_(False))
    ) or 0

    return {
        "total_alumnos": total_alumnos,
        "promedio_general": round(float(promedio_general), 2) if promedio_general is not None else None,
        "alertas_activas": alertas_activas,
        "inasistencias": inasistencias,
    }


@router.get("/alertas", response_model=list[AlertaRead])
def alertas_activas(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.DIRECTIVO)),
) -> list[AlertaRead]:
    return db.scalars(
        select(AlertaAprendizaje)
        .join(Alumno, AlertaAprendizaje.alumno_id == Alumno.id)
        .where(Alumno.colegio_id == current_user.colegio_id, AlertaAprendizaje.resuelta.is_(False))
        .order_by(AlertaAprendizaje.fecha.desc())
    ).all()


@router.get("/rendimiento", response_model=list[RendimientoCursoRead])
def rendimiento_por_curso(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.DIRECTIVO)),
) -> list[RendimientoCursoRead]:
    rows = db.execute(
        select(Alumno.curso, func.avg(Nota.valor), func.count(Nota.id))
        .join(Nota, Nota.alumno_id == Alumno.id)
        .where(Alumno.colegio_id == current_user.colegio_id)
        .group_by(Alumno.curso)
        .order_by(Alumno.curso.asc())
    ).all()

    return [
        {
            "curso": curso,
            "promedio": round(float(promedio), 2) if promedio is not None else None,
            "cantidad_notas": total,
        }
        for curso, promedio, total in rows
    ]
