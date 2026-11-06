from pydantic import BaseModel, Field


class IntegrantePlantel(BaseModel):
    ci_jugador: str = Field(pattern=r"^[0-9]{7,8}$")
    numero_camiseta: int = Field(..., ge=1, le=99, description="Número de camiseta entre 1 y 99")


class PlantelUpdate(BaseModel):
    integrantes: list[IntegrantePlantel]
    ci_capitan: str = Field(pattern=r"^[0-9]{7,8}$")


class JugadorPlantelOut(BaseModel):
    ci: str
    nombre: str
    apellido: str
    tipo: str
    numero_camiseta: int
    es_capitan: bool


class JugadorDisponibleOut(BaseModel):
    ci: str
    nombre: str
    apellido: str
    tipo: str


class PlantelOut(BaseModel):
    id_equipo: int
    integrantes: list[JugadorPlantelOut]
    ci_capitan: str | None = None
