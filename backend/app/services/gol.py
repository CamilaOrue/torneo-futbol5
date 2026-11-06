from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
import pymysql

from app.repositories import gol as repo


def _ahora():
    return datetime.now(timezone(timedelta(hours=-3)))


def _validar_partido(conn, id_partido):
    partido = repo.obtener_partido(conn, id_partido)

    if not partido:
        raise HTTPException(404, "El partido no existe.")

    if partido["estado"] == "cancelado":
        raise HTTPException(
            409,
            "No se pueden registrar goles en un partido cancelado."
        )

    hora_fin_td = partido["hora_fin"]
    fin_partido = datetime.combine(
        partido["dia"],
        (datetime.min + hora_fin_td).time()
    ).replace(tzinfo=timezone(timedelta(hours=-3)))

    ahora = _ahora()

    if ahora < fin_partido:
        raise HTTPException(
            409,
            "Solo se pueden registrar goles una vez finalizado el horario del partido."
        )

    if partido["estado"] == "jugado":
        limite = fin_partido + timedelta(hours=48)

        if ahora > limite:
            raise HTTPException(
                409,
                "Se superó el plazo de 48 horas para modificar los goles."
            )

    return partido


def _validar_jugador(conn, id_partido, ci_jugador):
    jugador = repo.jugador_en_planilla(
        conn,
        id_partido,
        ci_jugador
    )

    if not jugador:
        raise HTTPException(
            400,
            "El jugador no figura en la planilla de este partido."
        )


def _traducir(error):
    codigo = error.args[0] if error.args else None

    if codigo == 1452:
        raise HTTPException(
            400,
            "El jugador no está registrado en la planilla del partido."
        )

    if codigo == 3819:
        raise HTTPException(
            400,
            "El minuto del gol no cumple las restricciones permitidas."
        )

    raise HTTPException(
        500,
        "Ocurrió un error al operar con la base de datos."
    )


def listar(conn, id_partido):
    partido = repo.obtener_partido(conn, id_partido)
    if not partido:
        raise HTTPException(404, "El partido no existe.")
    return repo.listar(conn, id_partido)


def obtener(conn, id_gol):
    gol = repo.obtener(conn, id_gol)
    if not gol:
        raise HTTPException(404, "El gol no existe.")
    return gol


def registrar(conn, id_partido, datos):
    try:
        repo.bloquear_partido(conn, id_partido)
        _validar_partido(conn, id_partido)
        _validar_jugador(conn, id_partido, datos.ci_jugador)

        id_gol = repo.insertar(conn, id_partido, datos)
        conn.commit()
        return obtener(conn, id_gol)

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as error:
        conn.rollback()
        _traducir(error)
    except Exception as error:
        conn.rollback()
        raise


def actualizar(conn, id_gol, datos):
    try:
        gol = repo.obtener(conn, id_gol)
        if not gol:
            raise HTTPException(404, "El gol no existe.")

        repo.bloquear_partido(conn, gol["id_partido"])
        _validar_partido(conn, gol["id_partido"])
        _validar_jugador(conn, gol["id_partido"], datos.ci_jugador)

        repo.actualizar(conn, id_gol, datos)
        conn.commit()
        return obtener(conn, id_gol)

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as error:
        conn.rollback()
        _traducir(error)
    except Exception as error:
        conn.rollback()
        raise


def eliminar(conn, id_gol):
    try:
        gol = repo.obtener(conn, id_gol)
        if not gol:
            raise HTTPException(404, "El gol no existe.")

        repo.bloquear_partido(conn, gol["id_partido"])
        _validar_partido(conn, gol["id_partido"])

        repo.eliminar(conn, id_gol)
        conn.commit()

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as error:
        conn.rollback()
        _traducir(error)
    except Exception as error:
        conn.rollback()
        raise


def obtener_resultado(conn, id_partido):
    resultado = repo.resultado(conn, id_partido)
    if not resultado:
        raise HTTPException(404, "El partido no existe.")
    return resultado