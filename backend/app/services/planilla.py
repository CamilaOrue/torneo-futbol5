import pymysql
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import HTTPException

from app.repositories import planilla as repo
from app.repositories import sancion as sancion_repo


URUGUAY = ZoneInfo("America/Montevideo")


def _obtener_fin_partido(partido):
    """
    Combina el día del partido con la hora de finalización
    del turno y devuelve un datetime con zona horaria uruguaya.
    """
    return (
        datetime.combine(partido["dia"], datetime.min.time()) 
        + partido["hora_fin"]
    ).replace(tzinfo=URUGUAY)


def _validar_partido_para_planilla(partido):
    if partido["estado"] in ("cancelado", "postergado"):
        raise HTTPException(
            409,
            "No se puede registrar una planilla para un partido cancelado o postergado."
        )

    fin_partido = _obtener_fin_partido(partido)
    ahora = datetime.now(URUGUAY)

    if ahora < fin_partido:
        raise HTTPException(
            409,
            "La planilla solo se puede registrar una vez finalizado el horario del partido."
        )

    return fin_partido


def _validar_jugadores(conn, partido, ci_jugadores):
    # Buscar jugadores de cada equipo.
    jugadores_locales = repo.obtener_jugadores_equipo(
        conn,
        partido["id_equipo_local"],
        ci_jugadores
    )

    jugadores_visitantes = repo.obtener_jugadores_equipo(
        conn,
        partido["id_equipo_visitante"],
        ci_jugadores
    )

    # Un jugador solo puede pertenecer a uno de los dos equipos.
    jugadores_encontrados = jugadores_locales + jugadores_visitantes

    if len(jugadores_encontrados) != len(ci_jugadores):
        raise HTTPException(
            400,
            "Hay jugadores que no pertenecen al plantel de ninguno de los dos equipos del partido."
        )

    # Cada equipo debe tener al menos 5 participantes.
    if len(jugadores_locales) < 5:
        raise HTTPException(
            400,
            "El equipo local debe tener al menos 5 jugadores en la planilla."
        )

    if len(jugadores_visitantes) < 5:
        raise HTTPException(
            400,
            "El equipo visitante debe tener al menos 5 jugadores en la planilla."
        )

    # Comprobar que ninguno esté suspendido.
    for jugador in jugadores_encontrados:
        suspendido = sancion_repo.esta_suspendido(
            conn,
            jugador["ci_jugador"],
            partido["id_torneo"],
            partido["numero_fecha"]
        )

        if suspendido:
            raise HTTPException(
                409,
                f"El jugador {jugador['ci_jugador']} está suspendido para esta fecha."
            )

    return jugadores_encontrados


def listar(conn, id_partido):
    partido = repo.obtener_partido(conn, id_partido)

    if not partido:
        raise HTTPException(404, "El partido no existe.")

    return repo.listar(conn, id_partido)


def registrar(conn, id_partido, datos):
    try:
        # Bloquear el partido durante la operación.
        partido_bloqueado = repo.bloquear_partido(
            conn,
            id_partido
        )

        if not partido_bloqueado:
            raise HTTPException(404, "El partido no existe.")

        partido = repo.obtener_partido(conn, id_partido)

        fin_partido = _validar_partido_para_planilla(partido)

        # Si ya está jugado, solo permitimos corregir dentro de las 48 h.
        if partido["estado"] == "jugado":
            limite_correccion = fin_partido + timedelta(hours=48)

            if datetime.now(URUGUAY) > limite_correccion:
                raise HTTPException(
                    409,
                    "Se superó el plazo de 48 horas para corregir la planilla."
                )

        jugadores = _validar_jugadores(
            conn,
            partido,
            datos.ci_jugadores
        )

        # Verificar que no se eliminen jugadores con goles o tarjetas.
        planilla_actual = repo.listar(conn, id_partido)

        ci_nuevas = set(datos.ci_jugadores)

        for jugador in planilla_actual:
            if jugador["ci_jugador"] not in ci_nuevas:
                tiene_registros = repo.tiene_registros_asociados(
                    conn,
                    id_partido,
                    jugador["ci_jugador"]
                )

                if tiene_registros:
                    raise HTTPException(
                        409,
                        f"No se puede quitar al jugador {jugador['ci_jugador']} porque tiene goles o tarjetas registrados."
                    )

        # Quitar participantes que ya no están en la lista.
        repo.eliminar_no_incluidos(
            conn,
            id_partido,
            datos.ci_jugadores
        )

        # Agregar únicamente los jugadores nuevos.
        actuales = {
            jugador["ci_jugador"]
            for jugador in planilla_actual
        }

        for jugador in jugadores:
            if jugador["ci_jugador"] not in actuales:
                repo.insertar(
                    conn,
                    id_partido,
                    jugador["ci_jugador"],
                    jugador["id_equipo"]
                )

        conn.commit()

        return repo.listar(conn, id_partido)

    except HTTPException:
        conn.rollback()
        raise

    except Exception as error:
        conn.rollback()

        codigo = error.args[0] if error.args else None

        if codigo == 1062:
            raise HTTPException(
                409,
                "El jugador ya está registrado en la planilla."
            )

        if codigo == 1452:
            raise HTTPException(
                400,
                "El jugador o el partido indicado no existe."
            )

        if codigo == 1451:
            raise HTTPException(
                409,
                "No se puede modificar la planilla porque hay goles o tarjetas relacionados."
            )

        raise


def obtener_partido(conn, id_partido):
    partido = repo.obtener_partido(conn, id_partido)

    if not partido:
        raise HTTPException(404, "El partido no existe.")

    return partido