from typing import Literal
from pydantic import BaseModel, Field

Superficie = Literal["sintetico", "parquet"]


class CanchaCreate(BaseModel):
    nombre_cancha: str = Field(min_length=1, max_length=50)
    id_complejo: int = Field(ge=1)
    superficie: Superficie
    techada: bool = False


class CanchaOut(CanchaCreate):
    pass


class CanchaUpdate(BaseModel):
    superficie: Superficie
    techada: bool
