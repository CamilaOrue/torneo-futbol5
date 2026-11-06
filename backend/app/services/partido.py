from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
import pymysql

from app.repositories import partido as repo


def _ahora():
    # Establece una zona horaria fija segura de -3 (Montevideo UTC-3) para Docker Linux
    return datetime.now(timezone(timedelta(hours=-3)))


# ---------------------------------------------------------------- reglas de negocio
def _validar_programacion(conn, datos, id_partido=None):
    torneo = repo.bloquear_torneo(conn, datos.id_torneo)

    if not torneo:
        raise HTTPException(404, "El torneo no existe.")

    if torneo.get("estado") != "en curso":
        raise HTTPException(
            400, "Solo se pueden programar o modificar partidos en torneos en etapa 'en curso'."
        )

    local = repo.obtener_equipo(conn, datos.id_equipo_local, datos.id_torneo)
    visitante = repo.obtener_equipo(conn, datos.id_equipo_visitante, datos.id_torneo)

    if not local or not visitante:
        raise HTTPException(400, "Ambos equipos deben pertenecer al torneo indicado.")

    if datos.id_equipo_local == datos.id_equipo_visitante:
        raise HTTPException(400, "Un equipo no puede jugar contra sí mismo.")

    for id_equipo in (datos.id_equipo_local, datos.id_equipo_visitante):
        cantidad = repo.contar_jugadores(conn, id_equipo)
        if cantidad < 5:
            raise HTTPException(
                400, f"El equipo {id_equipo} necesita al menos 5 jugadores en su plantel."
            )

    anterior = repo.enfrentamiento_existente(
        conn,
        datos.id_torneo,
        datos.id_equipo_local,
        datos.id_equipo_visitante,
        excluir=id_partido,
    )

    if anterior:
        raise HTTPException(409, "Este enfrentamiento ya está registrado en la edición.")

    for id_equipo in (datos.id_equipo_local, datos.id_equipo_visitante):
        ocupado = repo.equipo_ya_juega_en_fecha(
            conn, id_equipo, datos.id_torneo, datos.numero_fecha, excluir=id_partido
        )
        if ocupado:
            raise HTTPException(
                409, f"El equipo {id_equipo} ya tiene un partido asignado en la fecha {datos.numero_fecha}."
            )

    if not repo.existe_turno(conn, datos.id_turno):
        raise HTTPException(404, "El turno indicado no existe.")

    if not repo.existe_cancha(conn, datos.nombre_cancha, datos.id_complejo):
        raise HTTPException(404, "La cancha indicada no existe en ese complejo.")

    ocupada = repo.cancha_ocupada(
        conn, datos.dia, datos.id_turno, datos.nombre_cancha, datos.id_complejo, excluir=id_partido
    )

    if ocupada:
        raise HTTPException(
            409, "La cancha ya tiene un partido asignado en ese día y turno."
        )


def _traducir(error):
    codigo = error.args[0] if error.args else None

    if codigo == 1062:
        raise HTTPException(409, "Ya existe un partido con esa combinación de cancha, día y turno.")
    if codigo == 1452:
        raise HTTPException(400, "Alguno de los registros relacionados (torneo, equipo, cancha) no existe.")
    if codigo == 1451:
        raise HTTPException(409, "No se puede eliminar el partido porque tiene planillas o goles asociados.")
    if codigo == 3819:
        raise HTTPException(400, "Los datos del partido no cumplen una restricción de la base de datos.")

    raise HTTPException(500, "Ocurrió un error inesperado al operar con la base de datos.")


def listar(conn, id_torneo=None, numero_fecha=None, estado=None):
    return repo.listar(conn, id_torneo, numero_fecha, estado)


def obtener(conn, id_partido):
    partido = repo.obtener(conn, id_partido)
    if not partido:
        raise HTTPException(404, "El partido no existe.")
    return partido


def crear(conn, datos):
    try:
        _validar_programacion(conn, datos)
        id_partido = repo.crear(conn, datos)
        conn.commit()
        return obtener(conn, id_partido)
    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as error:
        conn.rollback()
        _traducir(error)
        raise


def actualizar(conn, id_partido, datos):
    try:
        partido = repo.bloquear_partido(conn, id_partido)
        if not partido:
            raise HTTPException(404, "El partido no existe.")

        if partido["estado"] in ("jugado", "cancelado"):
            raise HTTPException(
                409, f"No se puede modificar la programación de un partido en estado '{partido['estado']}'."
            )

        class DatosValidacion:
            id_torneo = partido["id_torneo"]
            numero_fecha = datos.numero_fecha
            id_equipo_local = partido["id_equipo_local"]
            id_equipo_visitante = partido["id_equipo_visitante"]
            dia = datos.dia
            id_turno = datos.id_turno
            nombre_cancha = datos.nombre_cancha
            id_complejo = datos.id_complejo

        _validar_programacion(conn, DatosValidacion(), id_partido=id_partido)

        repo.actualizar_programacion(conn, id_partido, datos)
        conn.commit()

        return obtener(conn, id_partido)

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as error:
        conn.rollback()
        _traducir(error)
        raise


def cambiar_estado(conn, id_partido, nuevo_estado):
    try:
        partido = repo.bloquear_partido(conn, id_partido)
        if not partido:
            raise HTTPException(404, "El partido no existe.")

        estado_actual = partido["estado"]

        transiciones = {
            "programado": {"jugado", "postergado", "cancelado"},
            "postergado": {"jugado", "cancelado"},
            "jugado": set(),
            "cancelado": set(),
        }

        if nuevo_estado not in transiciones[estado_actual]:
            raise HTTPException(
                409, f"Transición no permitida: no se puede pasar de '{estado_actual}' a '{nuevo_estado}'."
            )

        if nuevo_estado == "jugado":
            # Extraemos la hora_fin del timedelta almacenado por mysql
            hora_fin_td = partido["hora_fin"]
            fin_partido = datetime.combine(
                partido["dia"], 
                (datetime.min + hora_fin_td).time()
            ).replace(tzinfo=timezone(timedelta(hours=-3)))

            if _ahora() < fin_partido:
                raise HTTPException(
                    409, "Un partido solo puede marcarse como jugado si su día y turno ya pasaron."
                )

        repo.actualizar_estado(conn, id_partido, nuevo_estado)
        conn.commit()

        return obtener(conn, id_partido)

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError:
        conn.rollback()
        raise


def eliminar(conn, id_partido):
    try:
        partido = repo.bloquear_partido(conn, id_partido)
        if not partido:
            raise HTTPException(404, "El partido no existe.")

        if partido["estado"] == "jugado":
            raise HTTPException(409, "Un partido jugado no puede eliminarse.")

        repo.eliminar(conn, id_partido)
        conn.commit()

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as error:
        conn.rollback()
        _traducir(error)
        raise


def obtener_resultado(conn, id_partido):
    partido = repo.obtener(conn, id_partido)
    if not partido:
        raise HTTPException(404, "El partido no existe.")
    return repo.goles_del_partido(conn, id_partido)
