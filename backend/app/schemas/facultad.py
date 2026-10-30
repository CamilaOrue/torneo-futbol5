from pydantic import BaseModel

class FacultadOut(BaseModel):
    id_facultad: int
    nombre: str
