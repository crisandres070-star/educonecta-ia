from __future__ import annotations

# pyright: reportMissingImports=false

from datetime import date, timedelta

import google.generativeai as genai
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models.alerta_aprendizaje import AlertaAprendizaje
from app.models.alumno import Alumno
from app.models.anotacion import Anotacion
from app.models.asistencia import Asistencia
from app.models.nota import Nota

genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    system_instruction=(
        "Eres EduConecta, un asistente IA especializado en educacion chilena. "
        "Tu rol es ayudar a los apoderados a entender el progreso de sus hijos de forma "
        "clara, empatica y accionable. Siempre hablas en espanol chileno, con lenguaje "
        "simple y calido. Nunca usas tecnicismos. Siempre propones acciones concretas."
    ),
)


def _serialize_context(alumno_id: int, db: Session, only_week: bool = False) -> dict:
    alumno = db.get(Alumno, alumno_id)
    if alumno is None:
        raise ValueError("Alumno no encontrado")

    start_week = date.today() - timedelta(days=7)
    notas_query = select(Nota).where(Nota.alumno_id == alumno_id)
    anotaciones_query = select(Anotacion).where(Anotacion.alumno_id == alumno_id)
    asistencias_query = select(Asistencia).where(Asistencia.alumno_id == alumno_id)

    if only_week:
        notas_query = notas_query.where(Nota.fecha >= start_week)
        anotaciones_query = anotaciones_query.where(Anotacion.fecha >= start_week)
        asistencias_query = asistencias_query.where(Asistencia.fecha >= start_week)

    notas = db.scalars(notas_query.order_by(Nota.fecha.desc())).all()
    anotaciones = db.scalars(anotaciones_query.order_by(Anotacion.fecha.desc())).all()
    asistencias = db.scalars(asistencias_query.order_by(Asistencia.fecha.desc())).all()
    alertas = db.scalars(
        select(AlertaAprendizaje)
        .where(AlertaAprendizaje.alumno_id == alumno_id)
        .order_by(AlertaAprendizaje.fecha.desc())
    ).all()

    return {
        "alumno": {
            "id": alumno.id,
            "nombre": alumno.nombre,
            "apellido": alumno.apellido,
            "curso": alumno.curso,
            "colegio_id": alumno.colegio_id,
        },
        "notas": [
            {
                "asignatura": n.asignatura,
                "valor": n.valor,
                "fecha": n.fecha.isoformat(),
                "descripcion": n.descripcion,
            }
            for n in notas
        ],
        "anotaciones": [
            {
                "tipo": a.tipo,
                "descripcion": a.descripcion,
                "fecha": a.fecha.isoformat(),
            }
            for a in anotaciones
        ],
        "asistencias": [
            {
                "fecha": a.fecha.isoformat(),
                "presente": a.presente,
                "justificada": a.justificada,
            }
            for a in asistencias
        ],
        "alertas": [
            {
                "tipo": a.tipo,
                "descripcion": a.descripcion,
                "detectada_por": a.detectada_por,
                "fecha": a.fecha.isoformat(),
                "resuelta": a.resuelta,
            }
            for a in alertas
        ],
    }


def _split_lines(text: str) -> list[str]:
    cleaned = text.replace("\r", "\n")
    lines = [line.strip(" -*0123456789.)") for line in cleaned.split("\n")]
    return [line for line in lines if line]


def generar_resumen_semanal(alumno_id: int, db: Session) -> str:
    context = _serialize_context(alumno_id, db, only_week=True)
    prompt = (
        "Genera un resumen semanal del alumno para su apoderado en lenguaje simple, "
        "con maximo 3 parrafos y cierre con acciones concretas.\n\n"
        f"Contexto: {context}"
    )
    try:
        response = model.generate_content(prompt)
        return (response.text or "No pude generar el resumen semanal en este momento.").strip()
    except Exception as exc:
        return f"No pude generar el resumen semanal por ahora. Intenta nuevamente en unos minutos. ({exc})"


def detectar_patrones(alumno_id: int, db: Session) -> list[str]:
    context = _serialize_context(alumno_id, db)
    prompt = (
        "Analiza el historial completo y detecta: tendencias de notas, patrones de inasistencia "
        "y posibles dificultades de aprendizaje. Devuelve una lista breve.\n\n"
        f"Contexto: {context}"
    )
    try:
        response = model.generate_content(prompt)
        text = (response.text or "").strip()
        items = _split_lines(text)
        return items if items else ["No se detectaron patrones claros por ahora."]
    except Exception as exc:
        return [f"No pude detectar patrones por ahora. Intenta nuevamente en unos minutos. ({exc})"]


def chat_apoderado(alumno_id: int, mensaje: str, historial: list[dict[str, str]] | None, db: Session) -> str:
    context = _serialize_context(alumno_id, db)
    historial = historial or []
    prompt = (
        "Responde la pregunta del apoderado usando el contexto del alumno y el historial del chat. "
        "Si no hay datos suficientes, dilo claramente y sugiere un siguiente paso.\n\n"
        f"Historial: {historial}\n"
        f"Mensaje: {mensaje}\n"
        f"Contexto: {context}"
    )
    try:
        response = model.generate_content(prompt)
        return (response.text or "No pude responder en este momento.").strip()
    except Exception as exc:
        return f"Ahora no pude responder con la IA. Intenta nuevamente en unos minutos. ({exc})"


def generar_recomendaciones(alumno_id: int, db: Session) -> list[str]:
    context = _serialize_context(alumno_id, db)
    prompt = (
        "Analiza toda la informacion del alumno y genera exactamente 3 recomendaciones concretas "
        "y accionables para el apoderado.\n\n"
        f"Contexto: {context}"
    )
    try:
        response = model.generate_content(prompt)
        text = (response.text or "").strip()
        items = _split_lines(text)
        if not items:
            return [
                "Conversar 10 minutos al dia sobre como se sintio en clases.",
                "Definir una rutina corta de estudio para la semana.",
                "Coordinar seguimiento con el profesor jefe.",
            ]
        return items[:3]
    except Exception as exc:
        return [f"No pude generar recomendaciones por ahora. Intenta nuevamente en unos minutos. ({exc})"]
