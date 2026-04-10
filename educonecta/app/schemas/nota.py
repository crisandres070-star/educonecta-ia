from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class NotaBase(BaseModel):
    alumno_id: int = Field(ge=1)
    asignatura: str = Field(min_length=2, max_length=120)
    valor: float = Field(ge=1.0, le=7.0)
    fecha: date
    descripcion: str | None = Field(default=None, max_length=500)

    model_config = ConfigDict(from_attributes=True)


class NotaCreate(NotaBase):
    model_config = ConfigDict(from_attributes=True)


class NotaRead(NotaBase):
    id: int
    profesor_id: int

    model_config = ConfigDict(from_attributes=True)
