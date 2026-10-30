from datetime import date
from typing import Literal

from pydantic import BaseModel

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
