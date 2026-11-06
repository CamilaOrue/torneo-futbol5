from typing import Optional

from fastapi import APIRouter, Depends, Response, status

from app.database import get_db_admin
from app.schemas.partido import (
    PartidoCreate,
    PartidoUpdate,
    PartidoEstadoUpdate,
    PartidoOut
)
from app.security import requiere_rol
from app.services import partido as service

# Consultar el fixture: administradores y planilleros. Programar, modificar o borrar: solo administradores.
router = APIRouter(
    prefix="/partidos",
    tags=["Partidos"],
    dependencies=[Depends(requiere_rol("administrador", "planillero"))],
)
solo_admin = [Depends(requiere_rol("administrador"))]


@router.get("/", response_model=list[PartidoOut])
def listar_partidos(
    id_torneo: Optional[int] = None,
    numero_fecha: Optional[int] = None,
    estado: Optional[str] = None,
    conn=Depends(get_db_admin)
):
    return service.listar(
        conn,
        id_torneo,
        numero_fecha,
        estado
    )


@router.get("/{id_partido}", response_model=PartidoOut)
def obtener_partido(
    id_partido: int,
    conn=Depends(get_db_admin)
):
    return service.obtener(conn, id_partido)


@router.post(
    "/",
    response_model=PartidoOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=solo_admin,
)
def crear_partido(
    datos: PartidoCreate,
    conn=Depends(get_db_admin)
):
    return service.crear(conn, datos)


@router.put("/{id_partido}", response_model=PartidoOut, dependencies=solo_admin)
def actualizar_partido(
    id_partido: int,
    datos: PartidoUpdate,
    conn=Depends(get_db_admin)
):
    return service.actualizar(conn, id_partido, datos)


@router.patch("/{id_partido}/estado", response_model=PartidoOut, dependencies=solo_admin)
def cambiar_estado_partido(
    id_partido: int,
    datos: PartidoEstadoUpdate,
    conn=Depends(get_db_admin)
):
    return service.cambiar_estado(
        conn,
        id_partido,
        datos.estado
    )


@router.delete(
    "/{id_partido}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=solo_admin,
)
def eliminar_partido(
    id_partido: int,
    conn=Depends(get_db_admin)
):
    service.eliminar(conn, id_partido)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
