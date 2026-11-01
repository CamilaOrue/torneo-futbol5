from pydantic import BaseModel, Field


class ComplejoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    direccion: str = Field(min_length=1, max_length=150)
    departamento: str = Field(min_length=1, max_length=50)


class ComplejoOut(ComplejoCreate):
    id_complejo: int
