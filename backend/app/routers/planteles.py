from fastapi import APIRouter, Depends, Path

from app.database import get_db_admin
from app.schemas.plantel import PlantelOut, PlantelUpdate
from app.services import plantel as service

router = APIRouter(prefix="/equipos/{id_equipo}/plantel", tags=["planteles"])


@router.get("", response_model=PlantelOut)
def obtener_plantel(
    id_equipo: int = Path(..., ge=1),
    conn=Depends(get_db_admin)
):
    return service.listar(conn, id_equipo)


@router.put("", response_model=PlantelOut)
def actualizar_plantel(
    datos: PlantelUpdate,
    id_equipo: int = Path(..., ge=1),
    conn=Depends(get_db_admin)
):
    return service.actualizar(conn, id_equipo, datos)