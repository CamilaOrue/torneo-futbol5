from fastapi import APIRouter, Depends
from pymysql.connections import Connection

from app.security import get_db_segun_rol, requiere_rol
from app.schemas.planilla import PlanillaCreate, PlanillaJugadorOut
from app.services import planilla as service


router = APIRouter(
    prefix="/planillas",
    tags=["Planillas"],
    dependencies=[Depends(requiere_rol("administrador", "planillero"))],
)


@router.get("/{id_partido}", response_model=list[PlanillaJugadorOut])
def obtener_planilla(
    id_partido: int,
    conn: Connection = Depends(get_db_segun_rol)
):
    return service.listar(conn, id_partido)


@router.put("/{id_partido}", response_model=list[PlanillaJugadorOut])
def registrar_planilla(
    id_partido: int,
    datos: PlanillaCreate,
    conn: Connection = Depends(get_db_segun_rol)
):
    return service.registrar(
        conn,
        id_partido,
        datos
    )