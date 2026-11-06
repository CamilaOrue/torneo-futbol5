from fastapi import APIRouter, Depends, Response, status
from pymysql.connections import Connection

from app.database import get_db_planillero
from app.schemas.tarjeta import TarjetaCreate, TarjetaUpdate, TarjetaOut, TarjetaDetalleOut
from app.services import tarjeta as service


router = APIRouter(
    prefix="/tarjetas",
    tags=["Tarjetas"]
)


@router.get("/partido/{id_partido}", response_model=list[TarjetaDetalleOut])
def listar_tarjetas(
    id_partido: int,
    conn: Connection = Depends(get_db_planillero)
):
    return service.listar(conn, id_partido)


@router.post(
    "/partido/{id_partido}",
    response_model=TarjetaOut,
    status_code=status.HTTP_201_CREATED
)
def registrar_tarjeta(
    id_partido: int,
    datos: TarjetaCreate,
    conn: Connection = Depends(get_db_planillero)
):
    return service.registrar(
        conn,
        id_partido,
        datos
    )


@router.get("/{id_tarjeta}", response_model=TarjetaOut)
def obtener_tarjeta(
    id_tarjeta: int,
    conn: Connection = Depends(get_db_planillero)
):
    return service.obtener(conn, id_tarjeta)


@router.put("/{id_tarjeta}", response_model=TarjetaOut)
def actualizar_tarjeta(
    id_tarjeta: int,
    datos: TarjetaUpdate,
    conn: Connection = Depends(get_db_planillero)
):
    return service.actualizar(
        conn,
        id_tarjeta,
        datos
    )


@router.delete(
    "/{id_tarjeta}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_tarjeta(
    id_tarjeta: int,
    conn: Connection = Depends(get_db_planillero)
):
    service.eliminar(conn, id_tarjeta)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
