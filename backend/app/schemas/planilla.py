from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints


CI = Annotated[
    str,
    StringConstraints(pattern=r"^[0-9]{7,8}$")
]


class PlanillaCreate(BaseModel):
    jugadores: list[CI] = Field(min_length=1)


class GolCreate(BaseModel):
    ci: CI
    minuto: int = Field(ge=0, le=60)
    autogol: bool = False


class TarjetaCreate(BaseModel):
    ci: CI
    minuto: int = Field(ge=0, le=60)
    color: Literal["amarilla", "roja"]