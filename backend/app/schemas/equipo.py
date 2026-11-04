from pydantic import BaseModel, ConfigDict, Field, field_validator

#--------------------------------------------------------------- entrada
class EquipoBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str
    id_facultad: int
    ci_capitan: str | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        if not v:
            raise ValueError("El nombre del equipo es obligatorio")
        if len(v) > 100:
            raise ValueError("Máximo 100 caracteres")
        return v

    @field_validator("id_facultad")
    @classmethod
    def _validar_facultad(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Seleccioná una facultad")
        return v


class EquipoCreate(EquipoBase):
    id_torneo: int

    @field_validator("id_torneo")
    @classmethod
    def _validar_torneo(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Seleccioná un torneo válido")
        return v


class EquipoUpdate(EquipoBase):
    """No se modifica el torneo al que pertenece el equipo."""


class CapitanUpdate(BaseModel):
    ci_capitan: str = Field(pattern=r"^[0-9]{7,8}$")


#--------------------------------------------------------------- salida
class EquipoOut(BaseModel):
    id_equipo: int
    nombre: str
    id_torneo: int
    torneo: str
    id_facultad: int
    facultad: str
    ci_capitan: str | None = None
    capitan: str | None = None
    cantidad_jugadores: int


class EquipoDetalleOut(EquipoOut):
    plantel: list["JugadorPlantelOut"]


# Se importa al final para evitar una dependencia circular entre schemas.
from app.schemas.plantel import JugadorPlantelOut