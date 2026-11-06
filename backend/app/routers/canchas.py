
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from app.database import get_db_admin
from app.schemas.cancha import CanchaCreate, CanchaOut, CanchaUpdate
from app.services import cancha as service

router = APIRouter(prefix="/canchas", tags=["canchas"])


@router.get("", response_model=list[CanchaOut])
def listar_canchas(
    id_complejo: Annotated[int | None, Query(ge=1)] = None,
    conn=Depends(get_db_admin)
):
    return service.listar(conn, id_complejo)


@router.get("/{id_complejo}/{nombre_cancha}", response_model=CanchaOut)
def obtener_cancha(
    id_complejo: int = Path(..., ge=1),
    nombre_cancha: str = Path(..., min_length=1, max_length=50),
    conn=Depends(get_db_admin)
):
    return service.obtener(conn, id_complejo, nombre_cancha)


@router.post("/{id_complejo}", response_model=CanchaOut, status_code=201)
def crear_cancha(
    id_complejo: int,
    datos: CanchaCreate,
    conn=Depends(get_db_admin)
):
    return service.crear(conn, id_complejo, datos)


@router.put("/{id_complejo}/{nombre_cancha}", response_model=CanchaOut)
def actualizar_cancha(
    datos: CanchaUpdate,
    id_complejo: int = Path(..., ge=1),
    nombre_cancha: str = Path(..., min_length=1, max_length=50),
    conn=Depends(get_db_admin)
):
    return service.actualizar(conn, nombre_cancha, id_complejo, datos)


@router.delete("/{id_complejo}/{nombre_cancha}", status_code=204)
def eliminar_cancha(
    id_complejo: int = Path(..., ge=1),
    nombre_cancha: str = Path(..., min_length=1, max_length=50),
    conn=Depends(get_db_admin)
):
    service.eliminar(conn, nombre_cancha, id_complejo)
    return Response(status_code=204)
