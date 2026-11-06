from typing import Optional

from app.security import requiere_rol

from fastapi import APIRouter, Depends, Response, status
from pymysql.connections import Connection

from app.database import get_db_admin
from app.schemas.sancion import (
    SancionCreate,
    SancionUpdate,
    SancionOut
)
from app.services import sancion as service


router = APIRouter(
    prefix="/sanciones",
    tags=["Sanciones"]
)


@router.get("/", response_model=list[SancionOut])
def listar_sanciones(
    id_torneo: Optional[int] = None,
    ci_jugador: Optional[str] = None,
    conn: Connection = Depends(get_db_admin)
):
    return service.listar(
        conn,
        id_torneo,
        ci_jugador
    )


@router.get("/{id_sancion}", response_model=SancionOut)
def obtener_sancion(
    id_sancion: int,
    conn: Connection = Depends(get_db_admin)
):
    return service.obtener(conn, id_sancion)


@router.post(
    "/",
    response_model=SancionOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(requiere_rol("administrador"))],
)
def crear_sancion(
    datos: SancionCreate,
    conn: Connection = Depends(get_db_admin)
):
    return service.crear(conn, datos)


@router.put(
    "/{id_sancion}",
    response_model=SancionOut,
    dependencies=[Depends(requiere_rol("administrador"))],
)
def actualizar_sancion(
    id_sancion: int,
    datos: SancionUpdate,
    conn: Connection = Depends(get_db_admin)
):
    return service.actualizar(
        conn,
        id_sancion,
        datos
    )


@router.delete(
    "/{id_sancion}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(requiere_rol("administrador"))],
)
def eliminar_sancion(
    id_sancion: int,
    conn: Connection = Depends(get_db_admin)
):
    service.eliminar(conn, id_sancion)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
