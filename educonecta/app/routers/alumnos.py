from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import require_roles
from app.models.alumno import Alumno
from app.models.user import User, UserRole
from app.schemas.alumno import AlumnoRead

router = APIRouter(prefix="/alumnos", tags=["Alumnos"])


@router.get("", response_model=list[AlumnoRead])
def listar_alumnos(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROFESOR, UserRole.DIRECTIVO)),
) -> list[AlumnoRead]:
    return db.scalars(select(Alumno).where(Alumno.colegio_id == current_user.colegio_id)).all()


@router.get("/{alumno_id}", response_model=AlumnoRead)
def obtener_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROFESOR, UserRole.DIRECTIVO, UserRole.APODERADO)),
) -> AlumnoRead:
    alumno = db.get(Alumno, alumno_id)
    if alumno is None:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    if current_user.rol == UserRole.APODERADO and alumno.apoderado_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sin permisos para ver este alumno")

    if current_user.rol != UserRole.APODERADO and alumno.colegio_id != current_user.colegio_id:
        raise HTTPException(status_code=403, detail="Sin permisos para ver este alumno")

    return alumno
