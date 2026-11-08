from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


SuperficieTipo = Literal["sintetico", "parquet"]

class CanchaBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre_cancha: str = Field(..., max_length=50, description="Nombre de la cancha")
    superficie: SuperficieTipo
    techada: bool = False

    @field_validator("nombre_cancha")
    @classmethod
    def validar_nombre(cls, valor):
        if not valor:
            raise ValueError("El nombre de la cancha no puede estar vacío")
        return valor


class CanchaCreate(CanchaBase):
    """Se utiliza cuando se crea una cancha dentro de un complejo."""


class CanchaUpdate(BaseModel):
    #model_config = ConfigDict(str_strip_whitespace=True)

    superficie: SuperficieTipo
    techada: bool = False


class CanchaOut(CanchaBase):
    id_complejo: int
    nombre_complejo: str | None = None
    superficie: str
    techada: bool