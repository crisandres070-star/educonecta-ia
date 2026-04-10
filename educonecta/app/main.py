import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import Base, engine
from app.models import alumno, anotacion, asistencia, colegio, nota, user
from app.models.alerta_aprendizaje import AlertaAprendizaje
from app.routers import alumnos, apoderados, auth, directivos, profesores

settings = get_settings()
port = int(os.environ.get("PORT", 8000))

app = FastAPI(title="EduConecta IA API", version="0.1.0", default_response_class=JSONResponse)


@app.middleware("http")
async def add_utf8_header(request, call_next):
    response = await call_next(request)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "EduConecta IA API activa"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(profesores.router)
app.include_router(apoderados.router)
app.include_router(alumnos.router)
app.include_router(directivos.router)
