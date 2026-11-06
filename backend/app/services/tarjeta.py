from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
import pymysql

from app.repositories import tarjeta as repo


def _ahora():
    return datetime.now(timezone(timedelta(hours=-3)))


def _validar_partido(partido):
    if partido["estado"] == "cancelado":
        raise HTTPException(
            409,
            "No se pueden registrar tarjetas en un partido cancelado."
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
            "Solo se pueden registrar tarjetas una vez finalizado el horario del partido."
        )

    if partido["estado"] == "jugado":
        if ahora > fin_partido + timedelta(hours=48):
            raise HTTPException(
                409,
                "Se superó el plazo de 48 horas para corregir las tarjetas."
            )


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


def _generar_sancion_si_corresponde(
    conn,
    partido,
    ci_jugador,
    color,
    id_tarjeta
):
    motivo = None

    if color == "roja":
        motivo = "roja"

    elif color == "amarilla":
        cantidad = repo.contar_amarillas_edicion(
            conn,
            ci_jugador,
            partido["id_torneo"]
        )

        if cantidad == 3:
            motivo = "acumulacion_amarillas"

    if motivo:
        repo.crear_sancion_automatica(
            conn,
            ci_jugador,
            partido["id_torneo"],
            motivo,
            partido["numero_fecha"] + 1,
            id_tarjeta
        )


def listar(conn, id_partido):
    partido = repo.obtener_partido(conn, id_partido)
    if not partido:
        raise HTTPException(404, "El partido no existe.")
    return repo.listar(conn, id_partido)


def registrar(conn, id_partido, datos):
    try:
        bloqueado = repo.bloquear_partido(conn, id_partido)
        if not bloqueado:
            raise HTTPException(404, "El partido no existe.")

        partido = repo.obtener_partido(conn, id_partido)
        _validar_partido(partido)
        _validar_jugador(conn, id_partido, datos.ci_jugador)

        id_tarjeta = repo.insertar(conn, id_partido, datos)

        _generar_sancion_si_corresponde(
            conn,
            partido,
            datos.ci_jugador,
            datos.color,
            id_tarjeta
        )

        conn.commit()
        return repo.obtener(conn, id_tarjeta)

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as error:
        conn.rollback()
        codigo = error.args[0] if error.args else None
        if codigo == 1452:
            raise HTTPException(400, "El jugador o el partido indicado no existe.")
        if codigo == 3819:
            raise HTTPException(400, "La tarjeta no cumple las restricciones de la base de datos.")
        raise HTTPException(500, "Error en la base de datos al registrar la tarjeta.")
    except Exception as error:
        conn.rollback()
        raise


def obtener(conn, id_tarjeta):
    tarjeta = repo.obtener(conn, id_tarjeta)
    if not tarjeta:
        raise HTTPException(404, "La tarjeta no existe.")
    return tarjeta


def actualizar(conn, id_tarjeta, datos):
    try:
        tarjeta = repo.obtener(conn, id_tarjeta)
        if not tarjeta:
            raise HTTPException(404, "La tarjeta no existe.")

        repo.bloquear_partido(conn, tarjeta["id_partido"])
        partido = repo.obtener_partido(conn, tarjeta["id_partido"])
        _validar_partido(partido)

        if repo.tiene_sancion_automatica_en_edicion(conn, tarjeta["ci_jugador"], partido["id_torneo"]):
            raise HTTPException(
                409,
                "El jugador tiene sanciones automáticas asociadas. La corrección de esta tarjeta debe realizarla un administrador revisando también sus sanciones."
            )

        if repo.tiene_sancion_automatica_en_edicion(conn, datos.ci_jugador, partido["id_torneo"]):
            raise HTTPException(
                409,
                "El jugador indicado tiene sanciones automáticas. No se puede reasignar esta tarjeta desde el planillero."
            )

        _validar_jugador(conn, tarjeta["id_partido"], datos.ci_jugador)

        repo.actualizar(conn, id_tarjeta, datos)
        conn.commit()
        return repo.obtener(conn, id_tarjeta)

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError:
        conn.rollback()
        raise
    except Exception:
        conn.rollback()
        raise


def eliminar(conn, id_tarjeta):
    try:
        tarjeta = repo.obtener(conn, id_tarjeta)
        if not tarjeta:
            raise HTTPException(404, "La tarjeta no existe.")

        repo.bloquear_partido(conn, tarjeta["id_partido"])
        partido = repo.obtener_partido(conn, tarjeta["id_partido"])
        _validar_partido(partido)

        sancion = repo.sancion_por_tarjeta(conn, id_tarjeta)
        if sancion:
            raise HTTPException(
                409,
                "Esta tarjeta generó una sanción automática. Un administrador debe revisar la sanción antes de eliminarla."
            )

        if repo.tiene_sancion_automatica_en_edicion(conn, tarjeta["ci_jugador"], partido["id_torneo"]):
            raise HTTPException(
                409,
                "El jugador tiene sanciones automáticas en esta edición. No se puede eliminar la tarjeta desde el planillero."
            )

        repo.eliminar(conn, id_tarjeta)
        conn.commit()

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError:
        conn.rollback()
        raise
    except Exception:
        conn.rollback()
        raise

