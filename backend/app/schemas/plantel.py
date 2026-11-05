from pydantic import BaseModel, Field, field_validator


class PlantelCreate(BaseModel):
    ci_jugador: str = Field(pattern=r"^[0-9]{7,8}$")
    numero_camiseta: int = Field(..., ge=1, le=99, description="Número de camiseta entre 1 y 99")


class PlantelUpdate(BaseModel):
    numero_camiseta: int = Field(..., ge=1, le=99, description="Número de camiseta entre 1 y 99")


class JugadorPlantelOut(BaseModel):
    ci: str
    nombre: str
    apellido: str
    tipo: str
    numero_camiseta: int
    es_capitan: bool