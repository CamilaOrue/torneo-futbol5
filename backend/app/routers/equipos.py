from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from app.database import get_db_admin
from app.schemas.equipo import EquipoCreate, EquipoDetalleOut, EquipoOut, EquipoUpdate
from app.services import equipo as service
from app.security import requiere_rol

router = APIRouter(
    prefix="/equipos",
    tags=["equipos"],
    dependencies=[Depends(requiere_rol("administrador", "planillero"))],
)

@router.get("", response_model=list[EquipoOut])
def listar_equipos(
    id_torneo: Annotated[int | None, Query(ge=1)] = None,
    id_facultad: Annotated[int | None, Query(ge=1)] = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
    conn=Depends(get_db_admin),
):
    return service.listar(conn, id_torneo, id_facultad, q)


@router.get("/{id_equipo}", response_model=EquipoDetalleOut)
def obtener_equipo(
    id_equipo: int = Path(..., ge=1),
    conn=Depends(get_db_admin)
):
    return service.obtener(conn, id_equipo)


@router.post("", response_model=EquipoOut, status_code=201)
def crear_equipo(
    datos: EquipoCreate,
    conn=Depends(get_db_admin)
):
    return service.crear(conn, datos)


@router.put("/{id_equipo}", response_model=EquipoOut)
def actualizar_equipo(
    datos: EquipoUpdate,
    id_equipo: int = Path(..., ge=1),
    conn=Depends(get_db_admin)
):
    return service.actualizar(conn, id_equipo, datos)


@router.delete("/{id_equipo}", status_code=204)
def eliminar_equipo(
    id_equipo: int = Path(..., ge=1),
    conn=Depends(get_db_admin)
):
    service.eliminar(conn, id_equipo)
    return Response(status_code=204)