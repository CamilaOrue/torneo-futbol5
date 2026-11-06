from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator

EstadoTorneo = Literal["inscripcion", "en curso", "finalizado"]


class TorneoOut(BaseModel):
    id_torneo: int
    nombre: str
    anio: int
    semestre: int
    fecha_inicio: date
    fecha_fin: date
    estado: EstadoTorneo
    cantidad_equipos: int
    cantidad_partidos: int
    partidos_jugados: int


# ---------------------------------------------------------------- entrada

class TorneoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    anio: int = Field(ge=2000, le=2100)
    semestre: Literal[1, 2]
    fecha_inicio: date
    fecha_fin: date

    # La fecha de fin tiene que ser posterior a la de inicio
    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("La fecha de fin debe ser posterior a la de inicio")
        return self


class TorneoEstadoUpdate(BaseModel):
    estado: EstadoTorneo