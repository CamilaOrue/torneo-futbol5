import re
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

TipoJugador = Literal["grado", "posgrado", "docente", "funcionario"]

# Además de letras (con tildes y ñ) se permiten espacios, apóstrofes, puntos y guiones.
_NOMBRE_EXTRA = set(" '.-")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_CI_RE = re.compile(r"^[0-9]{7,8}$")


def normalizar_ci(ci: str) -> str:
    """'1.234.567-8' -> '12345678'."""
    return re.sub(r"[.\-\s]", "", ci)


# ---------------------------------------------------------------- entrada
class JugadorBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str
    apellido: str
    email: str
    fecha_nacimiento: date
    id_facultad: int
    tipo: TipoJugador

    @field_validator("nombre", "apellido")
    @classmethod
    def _validar_nombre(cls, v: str) -> str:
        v = " ".join(v.split())
        if not v:
            raise ValueError("Este campo es obligatorio")
        if len(v) > 50:
            raise ValueError("Máximo 50 caracteres")
        # str.isalpha() equivale a \p{L} del front; [^\W\d_] aceptaba también "²", "½", "Ⅻ".
        if not any(c.isalpha() for c in v) or not all(c.isalpha() or c in _NOMBRE_EXTRA for c in v):
            raise ValueError("Solo puede contener letras, espacios, apóstrofes, puntos y guiones")
        return v

    @field_validator("email")
    @classmethod
    def _validar_email(cls, v: str) -> str:
        v = v.lower()
        if len(v) > 100:
            raise ValueError("Máximo 100 caracteres")
        if not _EMAIL_RE.match(v):
            raise ValueError("El email no tiene un formato válido")
        return v

    @field_validator("fecha_nacimiento")
    @classmethod
    def _validar_fecha(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError("La fecha de nacimiento debe ser anterior a hoy")
        if v.year < 1900:
            raise ValueError("La fecha de nacimiento no es válida")
        return v

    @field_validator("id_facultad")
    @classmethod
    def _validar_facultad(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Seleccioná una facultad")
        return v


class JugadorCreate(JugadorBase):
    ci: str

    @field_validator("ci")
    @classmethod
    def _validar_ci(cls, v: str) -> str:
        v = normalizar_ci(v)
        if not _CI_RE.match(v):
            raise ValueError("La CI debe tener 7 u 8 dígitos")
        return v


class JugadorUpdate(JugadorBase):
    """La CI es la clave primaria y no se modifica."""


# ---------------------------------------------------------------- salida
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
