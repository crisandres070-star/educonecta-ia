from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.anotacion import TipoAnotacion


class AnotacionBase(BaseModel):
    alumno_id: int = Field(ge=1)
    tipo: TipoAnotacion
    descripcion: str = Field(min_length=3, max_length=500)
    fecha: date

    model_config = ConfigDict(from_attributes=True)


class AnotacionCreate(AnotacionBase):
    model_config = ConfigDict(from_attributes=True)


class AnotacionRead(AnotacionBase):
    id: int
    profesor_id: int

    model_config = ConfigDict(from_attributes=True)
