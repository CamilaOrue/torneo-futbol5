from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from app.database import get_db_admin
from app.schemas.complejo import (
    ComplejoCreate,
    ComplejoOut,
    ComplejoUpdate
)
from app.services import complejo as service_complejo


router = APIRouter(
    prefix="/complejos",
    tags=["complejos"]
)


@router.get("", response_model=list[ComplejoOut])
def listar_complejos(
    q: Annotated[
        str | None,
        Query(max_length=100, description="Buscar por nombre o departamento")
    ] = None,
    conn=Depends(get_db_admin)
):
    return service_complejo.listar(conn, q)


@router.get("/{id_complejo}", response_model=ComplejoOut)
def obtener_complejo(
    id_complejo: int = Path(..., ge=1),
    conn=Depends(get_db_admin)
):
    return service_complejo.obtener(conn, id_complejo)


@router.post("", response_model=ComplejoOut, status_code=201)
def crear_complejo(
    datos: ComplejoCreate,
    conn=Depends(get_db_admin)
):
    return service_complejo.crear(conn, datos)


@router.put("/{id_complejo}", response_model=ComplejoOut)
def actualizar_complejo(
    datos: ComplejoUpdate,
    id_complejo: int = Path(..., ge=1),
    conn=Depends(get_db_admin)
):
    return service_complejo.actualizar(conn, id_complejo, datos)


@router.delete("/{id_complejo}", status_code=204)
def eliminar_complejo(
    id_complejo: int = Path(..., ge=1),
    conn=Depends(get_db_admin)
):
    service_complejo.eliminar(conn, id_complejo)
    return Response(status_code=204)
