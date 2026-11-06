from pydantic import BaseModel, Field


class GolCreate(BaseModel):
    ci_jugador: str = Field(min_length=7, max_length=8)
    minuto: int = Field(ge=0, le=60)
    autogol: bool = False


class GolUpdate(BaseModel):
    ci_jugador: str = Field(min_length=7, max_length=8)
    minuto: int = Field(ge=0, le=60)
    autogol: bool


class GolOut(BaseModel):
    id_gol: int
    id_partido: int
    ci_jugador: str
    minuto: int
    autogol: bool