from fastapi import APIRouter, Depends, Response, status
from pymysql.connections import Connection

from app.database import get_db_planillero
from app.schemas.gol import GolCreate, GolUpdate, GolOut, GolDetalleOut, ResultadoOut
from app.services import gol as service


router = APIRouter(
    prefix="/goles",
    tags=["Goles"]
)


@router.get("/partido/{id_partido}", response_model=list[GolDetalleOut])
def listar_goles(
    id_partido: int,
    conn: Connection = Depends(get_db_planillero)
):
    return service.listar(conn, id_partido)


@router.post(
    "/partido/{id_partido}",
    response_model=GolOut,
    status_code=status.HTTP_201_CREATED
)
def registrar_gol(
    id_partido: int,
    datos: GolCreate,
    conn: Connection = Depends(get_db_planillero)
):
    return service.registrar(
        conn,
        id_partido,
        datos
    )


@router.get("/resultado/{id_partido}", response_model=ResultadoOut)
def obtener_resultado(
    id_partido: int,
    conn: Connection = Depends(get_db_planillero)
):
    return service.obtener_resultado(conn, id_partido)


@router.get("/{id_gol}", response_model=GolOut)
def obtener_gol(
    id_gol: int,
    conn: Connection = Depends(get_db_planillero)
):
    return service.obtener(conn, id_gol)


@router.put("/{id_gol}", response_model=GolOut)
def actualizar_gol(
    id_gol: int,
    datos: GolUpdate,
    conn: Connection = Depends(get_db_planillero)
):
    return service.actualizar(
        conn,
        id_gol,
        datos
    )


@router.delete(
    "/{id_gol}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_gol(
    id_gol: int,
    conn: Connection = Depends(get_db_planillero)
):
    service.eliminar(conn, id_gol)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
