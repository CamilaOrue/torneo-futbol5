import pymysql
from fastapi import HTTPException

from app.repositories import cancha as repo
from app.repositories import complejo as repo_complejo
from app.schemas.cancha import CanchaCreate, CanchaUpdate


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


def obtener(conn, id_complejo: int, nombre_cancha: str):
    res = repo.obtener(conn, id_complejo, nombre_cancha)
    if not res:
        raise HTTPException(404, detail="Cancha no encontrada")
    return res


def crear(conn, id_complejo: int, datos: CanchaCreate):
    try:
        if not repo_complejo.obtener(conn, id_complejo):
            raise HTTPException(404, "El complejo especificado no existe.")

        repo.crear(conn, id_complejo, datos)
        conn.commit()

        # Invertimos el orden para coincidir con la firma del repository: (conn, id_complejo, nombre_cancha)
        return repo.obtener(conn, id_complejo, datos.nombre_cancha)

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)


def actualizar(conn, nombre_cancha, id_complejo, datos):
    try:
        # Verificamos si la cancha existe usando obtener en lugar de bloquear
        if not repo.obtener(conn, id_complejo, nombre_cancha):
            raise HTTPException(404, "No se encontró la cancha")

        repo.actualizar(
            conn,
            id_complejo,
            nombre_cancha,
            datos.model_dump()
        )

        resultado = repo.obtener(conn, id_complejo, nombre_cancha)
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
        # Reemplazo repo.bloquear por repo.obtener
        if not repo.obtener(conn, id_complejo, nombre_cancha):
            raise HTTPException(404, "No se encontró la cancha")

        repo.eliminar(conn, id_complejo, nombre_cancha)
        conn.commit()
        
    except HTTPException:
        conn.rollback()
        raise

    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)
        