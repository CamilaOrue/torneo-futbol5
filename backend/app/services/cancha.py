
import pymysql
from fastapi import HTTPException

from app.repositories import cancha as repo


def _traducir(e):
    codigo = e.args[0]

    if codigo == 1062:
        raise HTTPException(
            409,
            "Ya existe una cancha con ese nombre en este complejo"
        )

    if codigo in (1451, 1217):
        raise HTTPException(
            409,
            "No se puede eliminar la cancha porque tiene partidos asociados"
        )

    if codigo == 1452:
        raise HTTPException(404, "No se encontró el complejo")

    raise e


def listar(conn, id_complejo=None):
    return repo.listar(conn, id_complejo)


def obtener(conn, nombre_cancha, id_complejo):
    cancha = repo.obtener(conn, nombre_cancha, id_complejo)

    if not cancha:
        raise HTTPException(404, "No se encontró la cancha")

    return cancha


def crear(conn, datos):
    try:
        if not repo.existe_complejo(conn, datos.id_complejo):
            raise HTTPException(404, "No se encontró el complejo")

        repo.crear(conn, datos.model_dump())
        resultado = repo.obtener(
            conn, datos.nombre_cancha, datos.id_complejo
        )

        conn.commit()
        return resultado

    except HTTPException:
        conn.rollback()
        raise

    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)


def actualizar(conn, nombre_cancha, id_complejo, datos):
    try:
        if not repo.bloquear(conn, nombre_cancha, id_complejo):
            raise HTTPException(404, "No se encontró la cancha")

        repo.actualizar(
            conn,
            nombre_cancha,
            id_complejo,
            datos.model_dump()
        )

        resultado = repo.obtener(conn, nombre_cancha, id_complejo)
        conn.commit()
        return resultado

    except HTTPException:
        conn.rollback()
        raise

    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)


def eliminar(conn, nombre_cancha, id_complejo):
    try:
        if not repo.bloquear(conn, nombre_cancha, id_complejo):
            raise HTTPException(404, "No se encontró la cancha")

        repo.eliminar(conn, nombre_cancha, id_complejo)
        conn.commit()

    except HTTPException:
        conn.rollback()
        raise

    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)
