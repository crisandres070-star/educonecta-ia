from pydantic import BaseModel, ConfigDict


class DashboardRead(BaseModel):
    total_alumnos: int
    promedio_general: float | None
    alertas_activas: int
    inasistencias: int

    model_config = ConfigDict(from_attributes=True)


class RendimientoCursoRead(BaseModel):
    curso: str
    promedio: float | None
    cantidad_notas: int

    model_config = ConfigDict(from_attributes=True)
