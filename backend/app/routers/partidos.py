from typing import Optional

from fastapi import APIRouter, Depends, Response, status
from pymysql.connections import Connection

from app.database import get_db_admin
from app.schemas.partido import (
    PartidoCreate,
    PartidoUpdate,
    PartidoEstadoUpdate,
)
from app.services import partido as service


router = APIRouter(
    prefix="/partidos",
    tags=["Partidos"]
)


@router.get("/")
def listar_partidos(
    id_torneo: Optional[int] = None,
    numero_fecha: Optional[int] = None,
    estado: Optional[str] = None,
    conn: Connection = Depends(get_db_admin)
):
    return service.listar(
        conn,
        id_torneo,
        numero_fecha,
        estado
    )


@router.get("/{id_partido}")
def obtener_partido(
    id_partido: int,
    conn: Connection = Depends(get_db_admin)
):
    return service.obtener(conn, id_partido)


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_partido(
    datos: PartidoCreate,
    conn: Connection = Depends(get_db_admin)
):
    return service.crear(conn, datos)


@router.put("/{id_partido}")
def actualizar_partido(
    id_partido: int,
    datos: PartidoUpdate,
    conn: Connection = Depends(get_db_admin)
):
    return service.actualizar(conn, id_partido, datos)


@router.patch("/{id_partido}/estado")
def cambiar_estado_partido(
    id_partido: int,
    datos: PartidoEstadoUpdate,
    conn: Connection = Depends(get_db_admin)
):
    return service.cambiar_estado(
        conn,
        id_partido,
        datos.estado
    )


@router.delete(
    "/{id_partido}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_partido(
    id_partido: int,
    conn: Connection = Depends(get_db_admin)
):
    service.eliminar(conn, id_partido)
    return Response(status_code=status.HTTP_204_NO_CONTENT)