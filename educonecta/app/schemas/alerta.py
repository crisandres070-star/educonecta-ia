from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.alerta_aprendizaje import DetectadaPor, TipoAlerta


class AlertaBase(BaseModel):
    alumno_id: int = Field(ge=1)
    tipo: TipoAlerta
    descripcion: str = Field(min_length=3, max_length=600)
    fecha: date

    model_config = ConfigDict(from_attributes=True)


class AlertaManualCreate(AlertaBase):
    model_config = ConfigDict(from_attributes=True)


class AlertaRead(AlertaBase):
    id: int
    colegio_id: int
    detectada_por: DetectadaPor
    resuelta: bool

    model_config = ConfigDict(from_attributes=True)
