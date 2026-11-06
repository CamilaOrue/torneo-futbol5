from typing import Literal
from pydantic import BaseModel, Field


ColorTarjeta = Literal["amarilla", "roja"]


class TarjetaCreate(BaseModel):
    ci_jugador: str = Field(min_length=7, max_length=8)
    minuto: int = Field(ge=0, le=60)
    color: ColorTarjeta


class TarjetaUpdate(BaseModel):
    ci_jugador: str = Field(min_length=7, max_length=8)
    minuto: int = Field(ge=0, le=60)
    color: ColorTarjeta


class TarjetaOut(BaseModel):
    id_tarjeta: int
    id_partido: int
    ci_jugador: str
    minuto: int
    color: ColorTarjeta


class TarjetaDetalleOut(TarjetaOut):
    nombre: str
    apellido: str