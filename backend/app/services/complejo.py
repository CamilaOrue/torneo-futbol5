from fastapi import HTTPException
import pymysql

from app.errors import error_campo
from app.repositories import complejo as repo
from app.schemas.complejo import ComplejoCreate, ComplejoUpdate


def _traducir(e: pymysql.MySQLError):
    codigo = e.args[0]

    if codigo == 1062:
        raise error_campo(409, "nombre", "Ya existe un complejo deportivo registrado con ese nombre")
    
    if codigo in (1451, 1217):
        raise HTTPException(
            409, "No se puede eliminar el complejo porque tiene canchas o partidos asociados"
        )
    raise e

def listar(conn):
    return repo.listar(conn)


def obtener(conn, id_complejo: int):
    complejo = repo.obtener(conn, id_complejo)

    if not complejo:
        raise HTTPException(
            status_code=404, detail="No se encontró el complejo deportivo"
        )

    return complejo


def crear(conn, datos: ComplejoCreate):
    try:
        id_creado = repo.crear(conn, datos.model_dump())
        conn.commit()
        return obtener(conn, id_creado)
    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)


def actualizar(conn, id_complejo: int, datos: ComplejoUpdate):
    try:
        if not repo.bloquear(conn, id_complejo):
            raise HTTPException(404, "Complejo deportivo no encontrado")
        
        repo.actualizar(conn, id_complejo, datos.model_dump())
        conn.commit()
        return obtener(conn, id_complejo)
    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)


def eliminar(conn, id_complejo: int):
    try:
        if not repo.bloquear(conn, id_complejo):
            raise HTTPException(
                status_code=404,
                detail="Complejo deportivo no encontrado"
            )

        repo.eliminar(conn, id_complejo)
        conn.commit()

    except HTTPException:
        conn.rollback()
        raise

    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)

