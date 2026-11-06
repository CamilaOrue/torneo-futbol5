import pymysql
from fastapi import HTTPException

from app.repositories import complejo as repo


def _traducir(e):
    codigo = e.args[0] if e.args else None

    if codigo == 1062:
        raise HTTPException(
            409,
            "Ya existe un complejo deportivo con ese nombre registrado"
        )
    if codigo in (1451, 1217):
        raise HTTPException(
            409,
            "No se puede eliminar el complejo porque tiene canchas asociadas"
        )
    raise e


def listar(conn, q=None):
    return repo.listar(conn, q)


def obtener(conn, id_complejo: int):
    res = repo.obtener(conn, id_complejo)
    if not res:
        raise HTTPException(404, "No se encontró el complejo")
    return res


def crear(conn, datos):
    try:
        id_creado = repo.crear(conn, datos.model_dump())
        conn.commit()
        return repo.obtener(conn, id_creado)
    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)


def actualizar(conn, id_complejo: int, datos):
    try:
        if not repo.bloquear(conn, id_complejo):
            raise HTTPException(404, "No se encontró el complejo")

        repo.actualizar(conn, id_complejo, datos.model_dump())
        conn.commit()
        return repo.obtener(conn, id_complejo)
    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)


def eliminar(conn, id_complejo: int):
    try:
        if not repo.bloquear(conn, id_complejo):
            raise HTTPException(404, "No se encontró el complejo")

        repo.eliminar(conn, id_complejo)
        conn.commit()
    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)