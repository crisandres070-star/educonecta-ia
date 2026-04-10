from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import or_, select

from app.database import Base, SessionLocal, engine
from app.middleware.auth import hash_password
from app.models.alerta_aprendizaje import AlertaAprendizaje, DetectadaPor, TipoAlerta
from app.models.alumno import Alumno
from app.models.anotacion import Anotacion, TipoAnotacion
from app.models.asistencia import Asistencia
from app.models.colegio import Colegio
from app.models.nota import Nota
from app.models.user import User, UserRole


def get_or_create_colegio(db) -> Colegio:
    colegio = db.scalar(
        select(Colegio).where(or_(Colegio.nombre == "Colegio San Joaquín", Colegio.nombre == "Colegio San Joaquin"))
    )
    if colegio:
        return colegio

    colegio = Colegio(nombre="Colegio San Joaquín", ciudad="Santiago")
    db.add(colegio)
    db.flush()
    return colegio


def get_or_create_user(db, email: str, nombre: str, rol: UserRole, colegio_id: int) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user:
        user.nombre = nombre
        user.rol = rol
        user.colegio_id = colegio_id
        user.password_hash = hash_password("test1234")
        db.flush()
        return user

    user = User(
        email=email,
        password_hash=hash_password("test1234"),
        rol=rol,
        nombre=nombre,
        colegio_id=colegio_id,
    )
    db.add(user)
    db.flush()
    return user


def get_or_create_alumno(db, apoderado_id: int, colegio_id: int) -> Alumno:
    alumno = db.scalar(
        select(Alumno).where(
            or_(Alumno.nombre == "Matías", Alumno.nombre == "Matias"),
            Alumno.apellido == "Soto",
            Alumno.apoderado_id == apoderado_id,
        )
    )
    if alumno:
        return alumno

    alumno = Alumno(
        nombre="Matías",
        apellido="Soto",
        curso="7° Básico B",
        colegio_id=colegio_id,
        apoderado_id=apoderado_id,
    )
    db.add(alumno)
    db.flush()
    return alumno


def ensure_nota(db, alumno_id: int, profesor_id: int, colegio_id: int, asignatura: str, valor: float, fecha: date) -> None:
    exists = db.scalar(
        select(Nota.id).where(
            Nota.alumno_id == alumno_id,
            Nota.profesor_id == profesor_id,
            Nota.asignatura == asignatura,
            Nota.valor == valor,
            Nota.fecha == fecha,
        )
    )
    if exists:
        return

    db.add(
        Nota(
            alumno_id=alumno_id,
            profesor_id=profesor_id,
            colegio_id=colegio_id,
            asignatura=asignatura,
            valor=valor,
            fecha=fecha,
            descripcion=f"Evaluacion de {asignatura}",
        )
    )


def ensure_anotacion(
    db,
    alumno_id: int,
    profesor_id: int,
    colegio_id: int,
    tipo: TipoAnotacion,
    descripcion: str,
    fecha: date,
) -> None:
    exists = db.scalar(
        select(Anotacion.id).where(
            Anotacion.alumno_id == alumno_id,
            Anotacion.profesor_id == profesor_id,
            Anotacion.tipo == tipo,
            Anotacion.descripcion == descripcion,
            Anotacion.fecha == fecha,
        )
    )
    if exists:
        return

    db.add(
        Anotacion(
            alumno_id=alumno_id,
            profesor_id=profesor_id,
            colegio_id=colegio_id,
            tipo=tipo,
            descripcion=descripcion,
            fecha=fecha,
        )
    )


def ensure_asistencia(db, alumno_id: int, colegio_id: int, fecha: date, presente: bool, justificada: bool) -> None:
    exists = db.scalar(select(Asistencia.id).where(Asistencia.alumno_id == alumno_id, Asistencia.fecha == fecha))
    if exists:
        return

    db.add(
        Asistencia(
            alumno_id=alumno_id,
            colegio_id=colegio_id,
            fecha=fecha,
            presente=presente,
            justificada=justificada,
        )
    )


def ensure_alerta(db, alumno_id: int, colegio_id: int, fecha_alerta: date) -> None:
    descripcion = "4 observaciones de concentración esta semana"
    exists = db.scalar(
        select(AlertaAprendizaje.id).where(
            AlertaAprendizaje.alumno_id == alumno_id,
            AlertaAprendizaje.tipo == TipoAlerta.ATENCION,
            AlertaAprendizaje.descripcion == descripcion,
            AlertaAprendizaje.detectada_por == DetectadaPor.PROFESOR,
        )
    )
    if exists:
        return

    db.add(
        AlertaAprendizaje(
            alumno_id=alumno_id,
            colegio_id=colegio_id,
            tipo=TipoAlerta.ATENCION,
            descripcion=descripcion,
            detectada_por=DetectadaPor.PROFESOR,
            fecha=fecha_alerta,
            resuelta=False,
        )
    )


def build_weekdays(total_days: int) -> list[date]:
    days: list[date] = []
    cursor = date.today()
    while len(days) < total_days:
        if cursor.weekday() < 5:
            days.append(cursor)
        cursor -= timedelta(days=1)
    days.reverse()
    return days


def main() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        colegio = get_or_create_colegio(db)

        profesor = get_or_create_user(
            db,
            email="profesor@educonecta.cl",
            nombre="Carlos González",
            rol=UserRole.PROFESOR,
            colegio_id=colegio.id,
        )
        apoderado = get_or_create_user(
            db,
            email="apoderado@educonecta.cl",
            nombre="María Soto",
            rol=UserRole.APODERADO,
            colegio_id=colegio.id,
        )
        get_or_create_user(
            db,
            email="directivo@educonecta.cl",
            nombre="Ana Pérez",
            rol=UserRole.DIRECTIVO,
            colegio_id=colegio.id,
        )

        alumno = get_or_create_alumno(db, apoderado_id=apoderado.id, colegio_id=colegio.id)

        today = date.today()
        notas_plan = [
            ("Matemáticas", 4.1, today - timedelta(days=29)),
            ("Matemáticas", 3.8, today - timedelta(days=26)),
            ("Matemáticas", 4.5, today - timedelta(days=22)),
            ("Lenguaje", 6.4, today - timedelta(days=20)),
            ("Lenguaje", 6.1, today - timedelta(days=17)),
            ("Lenguaje", 6.7, today - timedelta(days=14)),
            ("Ciencias", 5.2, today - timedelta(days=12)),
            ("Ciencias", 5.0, today - timedelta(days=10)),
            ("Historia", 6.0, today - timedelta(days=8)),
            ("Historia", 5.8, today - timedelta(days=6)),
            ("Inglés", 5.5, today - timedelta(days=4)),
            ("Ed. Física", 6.8, today - timedelta(days=2)),
        ]
        for asignatura, valor, fecha_nota in notas_plan:
            ensure_nota(db, alumno.id, profesor.id, colegio.id, asignatura, valor, fecha_nota)

        weekdays = build_weekdays(23)
        absent_mondays = 0
        for dia in weekdays:
            if dia.weekday() == 0 and absent_mondays < 3:
                ensure_asistencia(db, alumno.id, colegio.id, dia, presente=False, justificada=False)
                absent_mondays += 1
            else:
                ensure_asistencia(db, alumno.id, colegio.id, dia, presente=True, justificada=False)

        anotaciones_plan = [
            (TipoAnotacion.NEGATIVA, "Interrupción en clase de matemáticas", today - timedelta(days=9)),
            (TipoAnotacion.POSITIVA, "Destacado en lenguaje", today - timedelta(days=7)),
            (TipoAnotacion.NEUTRA, "Dificultad atencional durante trabajo en grupo", today - timedelta(days=5)),
            (TipoAnotacion.NEUTRA, "Dificultad atencional en actividad individual", today - timedelta(days=3)),
        ]
        for tipo, descripcion, fecha_anotacion in anotaciones_plan:
            ensure_anotacion(db, alumno.id, profesor.id, colegio.id, tipo, descripcion, fecha_anotacion)

        ensure_alerta(db, alumno.id, colegio.id, today - timedelta(days=1))

        db.commit()

        print("Seed completado. Puedes hacer login con:")
        print("Profesor: profesor@educonecta.cl / test1234")
        print("Apoderado: apoderado@educonecta.cl / test1234")
        print("Directivo: directivo@educonecta.cl / test1234")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
