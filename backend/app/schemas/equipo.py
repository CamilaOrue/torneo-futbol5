from pydantic import BaseModel

from app.schemas.jugador import TipoJugador


class EquipoOut(BaseModel):
    id_equipo: int
    nombre: str
    id_torneo: int
    torneo: str
    id_facultad: int
    facultad: str
    ci_capitan: str | None
    capitan: str | None
    cantidad_jugadores: int


class IntegrantePlantel(BaseModel):
    ci: str
    nombre: str
    apellido: str
    tipo: TipoJugador
    numero_camiseta: int
    es_capitan: bool


class EquipoDetalleOut(EquipoOut):
    plantel: list[IntegrantePlantel]
