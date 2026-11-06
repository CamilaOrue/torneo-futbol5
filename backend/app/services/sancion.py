from fastapi import HTTPException

from app.repositories import sancion as repo


def _validar_jugador(conn, ci_jugador, id_torneo):
    inscripto = repo.jugador_inscripto_en_torneo(
        conn,
        ci_jugador,
        id_torneo
    )

    if not inscripto:
        raise HTTPException(
            400,
            "El jugador no está inscripto en ningún equipo de ese torneo."
        )


def _traducir_error_mysql(error):
    codigo = error.args[0] if error.args else None

    if codigo == 1452:
        raise HTTPException(
            400,
            "El jugador o el torneo indicado no existe."
        )

    if codigo == 3819:
        raise HTTPException(
            400,
            "La sanción no cumple las restricciones de la base de datos."
        )

    raise HTTPException(
        500,
        "Ocurrió un error al operar con la base de datos."
    )


def listar(conn, id_torneo=None, ci_jugador=None):
    return repo.listar(conn, id_torneo, ci_jugador)


def obtener(conn, id_sancion):
    sancion = repo.obtener(conn, id_sancion)

    if not sancion:
        raise HTTPException(404, "La sanción no existe.")

    return sancion


def crear(conn, datos):
    try:
        if datos.motivo != "disciplinaria":
            raise HTTPException(
                400,
                "Las sanciones por roja o acumulación de amarillas se generan automáticamente al registrar las tarjetas."
            )

        _validar_jugador(
            conn,
            datos.ci_jugador,
            datos.id_torneo
        )

        id_sancion = repo.crear(conn, datos)

        conn.commit()

        return obtener(conn, id_sancion)

    except HTTPException:
        conn.rollback()
        raise

    except Exception as error:
        conn.rollback()

        if error.args and isinstance(error.args[0], int):
            _traducir_error_mysql(error)

        raise


def actualizar(conn, id_sancion, datos):
    try:
        sancion = repo.bloquear(conn, id_sancion)

        if not sancion:
            raise HTTPException(404, "La sanción no existe.")

        repo.actualizar(conn, id_sancion, datos)

        conn.commit()

        return obtener(conn, id_sancion)

    except HTTPException:
        conn.rollback()
        raise

    except Exception as error:
        conn.rollback()

        if error.args and isinstance(error.args[0], int):
            _traducir_error_mysql(error)

        raise


def eliminar(conn, id_sancion):
    try:
        sancion = repo.bloquear(conn, id_sancion)

        if not sancion:
            raise HTTPException(404, "La sanción no existe.")

        repo.eliminar(conn, id_sancion)

        conn.commit()

    except HTTPException:
        conn.rollback()
        raise

    except Exception as error:
        conn.rollback()

        if error.args and isinstance(error.args[0], int):
            _traducir_error_mysql(error)

        raise