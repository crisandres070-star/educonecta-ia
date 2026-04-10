from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import require_roles
from app.models.alerta_aprendizaje import AlertaAprendizaje
from app.models.alumno import Alumno
from app.models.nota import Nota
from app.models.user import User, UserRole
from app.schemas.alerta import AlertaRead
from app.schemas.nota import NotaRead
from app.services.ai_agent import chat_apoderado, generar_recomendaciones, generar_resumen_semanal

router = APIRouter(prefix="/apoderado", tags=["Apoderados"])


class ChatRequest(BaseModel):
    alumno_id: int = Field(ge=1)
    mensaje: str = Field(min_length=1, max_length=2000)
    historial: list[dict[str, str]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AlumnoResumen(BaseModel):
    id: int
    nombre: str
    apellido: str
    curso: str

    model_config = ConfigDict(from_attributes=True)


class ResumenHijoResponse(BaseModel):
    alumno: AlumnoResumen
    resumen: str

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    respuesta: str

    model_config = ConfigDict(from_attributes=True)


class RecomendacionesResponse(BaseModel):
    recomendaciones: list[str]

    model_config = ConfigDict(from_attributes=True)


def _validar_hijo(alumno_id: int, current_user: User, db: Session) -> Alumno:
    alumno = db.get(Alumno, alumno_id)
    if alumno is None or alumno.apoderado_id != current_user.id:
        raise HTTPException(status_code=404, detail="Alumno no encontrado para este apoderado")
    return alumno


@router.get("/mi-hijo/{alumno_id}", response_model=ResumenHijoResponse)
def resumen_hijo(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.APODERADO)),
) -> ResumenHijoResponse:
    alumno = _validar_hijo(alumno_id, current_user, db)
    resumen_ia = generar_resumen_semanal(alumno_id, db)
    return {
        "alumno": {
            "id": alumno.id,
            "nombre": alumno.nombre,
            "apellido": alumno.apellido,
            "curso": alumno.curso,
        },
        "resumen": resumen_ia,
    }


@router.get("/notas/{alumno_id}", response_model=list[NotaRead])
def historial_notas(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.APODERADO)),
) -> list[NotaRead]:
    _validar_hijo(alumno_id, current_user, db)
    return db.scalars(select(Nota).where(Nota.alumno_id == alumno_id).order_by(Nota.fecha.desc())).all()


@router.get("/alertas/{alumno_id}", response_model=list[AlertaRead])
def alertas_activas(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.APODERADO)),
) -> list[AlertaRead]:
    _validar_hijo(alumno_id, current_user, db)
    return db.scalars(
        select(AlertaAprendizaje)
        .where(AlertaAprendizaje.alumno_id == alumno_id, AlertaAprendizaje.resuelta.is_(False))
        .order_by(AlertaAprendizaje.fecha.desc())
    ).all()


@router.post("/chat", response_model=ChatResponse)
def chat_con_agente(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.APODERADO)),
) -> ChatResponse:
    _validar_hijo(payload.alumno_id, current_user, db)
    respuesta = chat_apoderado(payload.alumno_id, payload.mensaje, payload.historial, db)
    return {"respuesta": respuesta}


@router.get("/recomendaciones/{alumno_id}", response_model=RecomendacionesResponse)
def recomendaciones_ia(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.APODERADO)),
) -> RecomendacionesResponse:
    _validar_hijo(alumno_id, current_user, db)
    recomendaciones = generar_recomendaciones(alumno_id, db)
    return {"recomendaciones": recomendaciones}
