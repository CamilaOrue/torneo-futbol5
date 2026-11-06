from pydantic import BaseModel

from app.schemas.jugador import TipoJugador


#--------------------------------------------------------------- salida
# Un jugador dentro del plantel de un equipo (repositories/equipo.py -> plantel).
class JugadorPlantelOut(BaseModel):
    ci: str
    nombre: str
    apellido: str
    tipo: TipoJugador
    id_facultad: int
    numero_camiseta: int
    es_capitan: bool  # MySQL lo devuelve como 0/1; Pydantic lo pasa a True/False
