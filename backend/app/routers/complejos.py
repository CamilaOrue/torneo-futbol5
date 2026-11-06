from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response

from app.database import get_db_admin
from app.schemas.complejo import ComplejoCreate, ComplejoOut, ComplejoUpdate
from app.security import get_db_segun_rol, requiere_rol
from app.services import complejo as service_complejo


# Consultar: administradores y planilleros. Crear, modificar o borrar: solo administradores.
router = APIRouter(
    prefix="/complejos",
    tags=["complejos"],
    dependencies=[Depends(requiere_rol("administrador", "planillero"))],
)
solo_admin = [Depends(requiere_rol("administrador"))]


@router.get("", response_model=list[ComplejoOut])
def listar_complejos(
    q: Annotated[
        str | None,
        Query(max_length=100, description="Buscar por nombre o departamento")
    ] = None,
    conn=Depends(get_db_segun_rol)
):
    return service_complejo.listar(conn, q)


@router.get("/{id_complejo}", response_model=ComplejoOut)
def obtener_complejo(
    id_complejo: int = Path(..., ge=1),
    conn=Depends(get_db_segun_rol)
):
    return service_complejo.obtener(conn, id_complejo)


@router.post("", response_model=ComplejoOut, status_code=201, dependencies=solo_admin)
def crear_complejo(
    datos: ComplejoCreate,
    conn=Depends(get_db_admin)
):
    return service_complejo.crear(conn, datos)


@router.put("/{id_complejo}", response_model=ComplejoOut, dependencies=solo_admin)
def actualizar_complejo(
    datos: ComplejoUpdate,
    id_complejo: int = Path(..., ge=1),
    conn=Depends(get_db_admin)
):
    return service_complejo.actualizar(conn, id_complejo, datos)


@router.delete("/{id_complejo}", status_code=204, dependencies=solo_admin)
def eliminar_complejo(
    id_complejo: int = Path(..., ge=1),
    conn=Depends(get_db_admin)
):
    service_complejo.eliminar(conn, id_complejo)
    return Response(status_code=204)
