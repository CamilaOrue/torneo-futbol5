from datetime import date
from typing import Literal

from pydantic import BaseModel

TipoJugador = Literal["grado", "posgrado", "docente", "funcionario"]


class JugadorOut(BaseModel):
    ci: str
    nombre: str
    apellido: str
    email: str
    fecha_nacimiento: date
    id_facultad: int
    facultad: str
    tipo: TipoJugador
    equipo_actual: str | None = None


class EquipoHistorial(BaseModel):
    id_equipo: int
    equipo: str
    id_torneo: int
    torneo: str
    numero_camiseta: int


class JugadorDetalleOut(JugadorOut):
    equipos: list[EquipoHistorial]
