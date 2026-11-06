from typing import Literal
from pydantic import BaseModel, Field


MotivoSancion = Literal[
    "roja",
    "acumulacion_amarillas",
    "disciplinaria"
]


class SancionCreate(BaseModel):
    ci_jugador: str = Field(min_length=7, max_length=8)
    id_torneo: int = Field(gt=0)
    motivo: MotivoSancion
    numero_fecha_inicio: int = Field(ge=1, le=255)
    cantidad_fechas: int = Field(default=1, ge=1, le=255)


class SancionUpdate(BaseModel):
    motivo: MotivoSancion
    numero_fecha_inicio: int = Field(ge=1, le=255)
    cantidad_fechas: int = Field(ge=1, le=255)


class SancionOut(BaseModel):
    id_sancion: int
    ci_jugador: str
    id_torneo: int
    motivo: MotivoSancion
    numero_fecha_inicio: int
    cantidad_fechas: int
    nombre: str | None = None
    apellido: str | None = None
    nombre_torneo: str | None = None