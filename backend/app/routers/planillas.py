from fastapi import APIRouter, Depends
from pymysql.connections import Connection

from app.database import get_db_planillero
from app.schemas.planilla import PlanillaCreate, PlanillaJugadorOut
from app.services import planilla as service


router = APIRouter(
    prefix="/planillas",
    tags=["Planillas"]
)


@router.get("/{id_partido}", response_model=list[PlanillaJugadorOut])
def obtener_planilla(
    id_partido: int,
    conn: Connection = Depends(get_db_planillero)
):
    return service.listar(conn, id_partido)


@router.put("/{id_partido}", response_model=list[PlanillaJugadorOut])
def registrar_planilla(
    id_partido: int,
    datos: PlanillaCreate,
    conn: Connection = Depends(get_db_planillero)
):
    return service.registrar(
        conn,
        id_partido,
        datos
    )