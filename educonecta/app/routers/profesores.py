from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import require_roles
from app.models.alerta_aprendizaje import AlertaAprendizaje, DetectadaPor, TipoAlerta
from app.models.alumno import Alumno
from app.models.anotacion import Anotacion
from app.models.asistencia import Asistencia
from app.models.nota import Nota
from app.models.user import User, UserRole
from app.schemas.alerta import AlertaManualCreate, AlertaRead
from app.schemas.anotacion import AnotacionCreate, AnotacionRead
from app.schemas.asistencia import AsistenciaCreate, AsistenciaRead
from app.schemas.nota import NotaCreate, NotaRead

router = APIRouter(prefix="/profesor", tags=["Profesores"])


@router.post("/notas", response_model=NotaRead, status_code=status.HTTP_201_CREATED)
def ingresar_nota(
    payload: NotaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROFESOR)),
) -> NotaRead:
    nota = Nota(
        alumno_id=payload.alumno_id,
        colegio_id=current_user.colegio_id,
        asignatura=payload.asignatura,
        valor=payload.valor,
        profesor_id=current_user.id,
        fecha=payload.fecha,
        descripcion=payload.descripcion,
    )
    db.add(nota)
    db.commit()
    db.refresh(nota)
    return nota


@router.post("/anotaciones", response_model=AnotacionRead, status_code=status.HTTP_201_CREATED)
def ingresar_anotacion(
    payload: AnotacionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROFESOR)),
) -> AnotacionRead:
    anotacion = Anotacion(
        alumno_id=payload.alumno_id,
        colegio_id=current_user.colegio_id,
        tipo=payload.tipo,
        descripcion=payload.descripcion,
        profesor_id=current_user.id,
        fecha=payload.fecha,
    )
    db.add(anotacion)
    db.commit()
    db.refresh(anotacion)
    return anotacion


@router.post("/asistencia", response_model=AsistenciaRead, status_code=status.HTTP_201_CREATED)
def marcar_asistencia(
    payload: AsistenciaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROFESOR)),
) -> AsistenciaRead:
    asistencia = Asistencia(**payload.model_dump(), colegio_id=current_user.colegio_id)
    db.add(asistencia)
    db.commit()
    db.refresh(asistencia)
    return asistencia


@router.get("/mis-alumnos", response_model=list[dict])
def listar_mis_alumnos(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROFESOR)),
) -> list[dict]:
    alumnos = db.scalars(select(Alumno).where(Alumno.colegio_id == current_user.colegio_id)).all()
    return [
        {
            "id": a.id,
            "nombre": a.nombre,
            "apellido": a.apellido,
            "curso": a.curso,
            "apoderado_id": a.apoderado_id,
        }
        for a in alumnos
    ]


@router.post("/alertas", response_model=AlertaRead, status_code=status.HTTP_201_CREATED)
def crear_alerta_manual(
    payload: AlertaManualCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROFESOR)),
) -> AlertaRead:
    alerta = AlertaAprendizaje(
        alumno_id=payload.alumno_id,
        colegio_id=current_user.colegio_id,
        tipo=payload.tipo,
        descripcion=payload.descripcion,
        detectada_por=DetectadaPor.PROFESOR,
        fecha=payload.fecha,
        resuelta=False,
    )
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    return alerta
