from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AlumnoBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    apellido: str = Field(min_length=2, max_length=120)
    curso: str = Field(min_length=1, max_length=50)
    colegio_id: int = Field(ge=1)
    apoderado_id: int = Field(ge=1)

    model_config = ConfigDict(from_attributes=True)


class AlumnoCreate(AlumnoBase):
    model_config = ConfigDict(from_attributes=True)


class AlumnoRead(AlumnoBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
