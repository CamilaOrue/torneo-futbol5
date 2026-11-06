import pymysql

from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db_admin
from app.services import planilla as service
from app.schemas.planilla import PlanillaCreate, GolCreate, TarjetaCreate


router = APIRouter(prefix="/planilla", tags=["planilla"])


def _traducir(e: pymysql.MySQLError) -> HTTPException | None:
    codigo = e.args[0]

    if codigo == 1062:
        return HTTPException(409, "El registro ya existe")

    if codigo == 1452:
        return HTTPException(422, "El partido, jugador o equipo indicado no existe")

    if codigo == 3819:
        return HTTPException(422, "Los datos no cumplen las restricciones de la base de datos")

    return None


# --------------------------------------------------------------- planilla

@router.post("/{id_partido}/jugadores", status_code=201)
def guardar_planilla(
    id_partido: int,
    datos: PlanillaCreate,
    conn=Depends(get_db_admin),
):
    try:
        service.guardar_planilla(conn, id_partido, datos.jugadores)
        conn.commit()

    except ValueError as e:
        conn.rollback()
        raise HTTPException(409, str(e)) from e

    except pymysql.MySQLError as e:
        conn.rollback()
        http = _traducir(e)
        if http:
            raise http from e
        raise

    return {"mensaje": "Planilla guardada correctamente"}


# ------------------------------------------------------------------- goles

@router.post("/{id_partido}/goles", status_code=201)
def registrar_gol(
    id_partido: int,
    datos: GolCreate,
    conn=Depends(get_db_admin),
):
    try:
        id_gol = service.registrar_gol(
            conn, id_partido, datos.ci, datos.minuto, datos.autogol
        )
        conn.commit()

    except ValueError as e:
        conn.rollback()
        raise HTTPException(409, str(e)) from e

    except pymysql.MySQLError as e:
        conn.rollback()
        http = _traducir(e)
        if http:
            raise http from e
        raise

    return {"id_gol": id_gol}



@router.delete("/goles/{id_gol}", status_code=204)
def eliminar_gol(
    id_gol: int,
    conn=Depends(get_db_admin)
):
    # TODO: requiere_rol("administrador")
    try:
        service.eliminar_gol(conn, id_gol)
        conn.commit()
    except ValueError as e:
        conn.rollback()
        raise HTTPException(status_code=409, detail=str(e))
    except pymysql.MySQLError as e:
        conn.rollback()
        error = _traducir(e)
        if error:
            raise error
        raise



# --------------------------------------------------------------- tarjetas

@router.post("/{id_partido}/tarjetas", status_code=201)
def registrar_tarjeta(
    id_partido: int,
    datos: TarjetaCreate,
    conn=Depends(get_db_admin),
):
    try:
        id_tarjeta = service.registrar_tarjeta(
            conn, id_partido, datos.ci, datos.minuto, datos.color
        )
        conn.commit()

    except ValueError as e:
        conn.rollback()
        raise HTTPException(409, str(e)) from e

    except pymysql.MySQLError as e:
        conn.rollback()
        http = _traducir(e)
        if http:
            raise http from e
        raise

    return {"id_tarjeta": id_tarjeta}


