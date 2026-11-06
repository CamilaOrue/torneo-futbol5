from typing import List
from pydantic import BaseModel, Field, field_validator


class PlanillaCreate(BaseModel):
    ci_jugadores: List[str] = Field(
        min_length=10,
        max_length=20,
        description="Lista de cédulas de los jugadores que integran la planilla (mínimo 10, máximo 20)."
    )

    @field_validator("ci_jugadores")
    @classmethod
    def validar_cedulas_unicas(cls, valores):
        if len(valores) != len(set(valores)):
            raise ValueError(
                "No se puede incluir dos veces al mismo jugador."
            )

        for ci in valores:
            if not ci.isdigit() or len(ci) not in (7, 8):
                raise ValueError(
                    f"La cédula {ci} no tiene un formato válido."
                )

        return valores


class PlanillaJugadorOut(BaseModel):
    id_partido: int
    ci_jugador: str
    id_equipo: int
    nombre: str
    apellido: str