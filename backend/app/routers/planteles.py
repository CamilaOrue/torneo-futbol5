from fastapi import APIRouter, Depends, Path, Response

from app.database import get_db_admin
from app.schemas.plantel import IntegrantePlantel, JugadorDisponibleOut, PlantelOut, PlantelUpdate
from app.security import requiere_rol
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


@router.get("/disponibles", response_model=list[JugadorDisponibleOut])
def jugadores_disponibles(
    id_equipo: int = Path(..., ge=1),
    conn=Depends(get_db_admin),
):
    """Jugadores que se pueden sumar al plantel del equipo."""
    return service.disponibles(conn, id_equipo)


@router.post(
    "",
    response_model=PlantelOut,
    status_code=201,
    dependencies=[Depends(requiere_rol("administrador"))],
)
def agregar_integrante(
    datos: IntegrantePlantel,
    id_equipo: int = Path(..., ge=1),
    conn=Depends(get_db_admin),
):
    return service.agregar_integrante(conn, id_equipo, datos)


@router.delete(
    "/{ci}",
    status_code=204,
    dependencies=[Depends(requiere_rol("administrador"))],
)
def quitar_integrante(
    id_equipo: int = Path(..., ge=1),
    ci: str = Path(..., pattern=r"^[0-9]{7,8}$"),
    conn=Depends(get_db_admin),
):
    service.quitar_integrante(conn, id_equipo, ci)
    return Response(status_code=204)
