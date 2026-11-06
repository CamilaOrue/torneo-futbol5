from datetime import date, timedelta
from pydantic import BaseModel, Field
from typing import Literal

EstadoPartido = Literal[
    "programado",
    "jugado",
    "postergado",
    "cancelado"
]

class PartidoCreate(BaseModel):
    id_torneo: int = Field(gt=0)
    numero_fecha: int = Field(ge=1, le=255)
    id_equipo_local: int = Field(gt=0)
    id_equipo_visitante: int = Field(gt=0)
    dia: date
    id_turno: int = Field(gt=0)
    nombre_cancha: str = Field(min_length=1, max_length=50)
    id_complejo: int = Field(gt=0)


class PartidoUpdate(BaseModel):
    numero_fecha: int = Field(ge=1, le=255)
    dia: date
    id_turno: int = Field(gt=0)
    nombre_cancha: str = Field(min_length=1, max_length=50)
    id_complejo: int = Field(gt=0)


class PartidoEstadoUpdate(BaseModel):
    estado: EstadoPartido


class PartidoOut(BaseModel):
    id_partido: int
    id_torneo: int
    numero_fecha: int
    id_equipo_local: int
    id_equipo_visitante: int
    dia: date
    id_turno: int
    nombre_cancha: str
    id_complejo: int
    estado: EstadoPartido
    hora_inicio: timedelta
    hora_fin: timedelta
    