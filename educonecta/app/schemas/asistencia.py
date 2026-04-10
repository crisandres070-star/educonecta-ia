from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class AsistenciaBase(BaseModel):
    alumno_id: int = Field(ge=1)
    fecha: date
    presente: bool
    justificada: bool = False

    model_config = ConfigDict(from_attributes=True)


class AsistenciaCreate(AsistenciaBase):
    model_config = ConfigDict(from_attributes=True)


class AsistenciaRead(AsistenciaBase):
    id: int
    colegio_id: int

    model_config = ConfigDict(from_attributes=True)
