def obtener_partido(conn, id_partido):
    sql = """
        SELECT
            p.id_partido,
            p.id_torneo,
            p.numero_fecha,
            p.id_equipo_local,
            p.id_equipo_visitante,
            p.dia,
            p.id_turno,
            p.estado,
            t.hora_inicio,
            t.hora_fin
        FROM partido p
        JOIN turno t ON t.id_turno = p.id_turno
        WHERE p.id_partido = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_partido,))
        return cursor.fetchone()


def bloquear_partido(conn, id_partido):
    sql = """
        SELECT id_partido
        FROM partido
        WHERE id_partido = %s
        FOR UPDATE
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_partido,))
        return cursor.fetchone()


def obtener_jugadores_equipo(conn, id_equipo, ci_jugadores):
    """
    Busca cuáles de las cédulas enviadas pertenecen
    al plantel del equipo indicado.
    """
    if not ci_jugadores:
        return []

    placeholders = ", ".join(["%s"] * len(ci_jugadores))

    sql = f"""
        SELECT
            ej.ci_jugador,
            ej.id_equipo,
            j.nombre,
            j.apellido
        FROM equipo_jugador_torneo ej
        JOIN jugador j ON j.ci = ej.ci_jugador
        WHERE ej.id_equipo = %s
          AND ej.ci_jugador IN ({placeholders})
    """

    params = [id_equipo] + ci_jugadores

    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()


def listar(conn, id_partido):
    sql = """
        SELECT
            pp.id_partido,
            pp.ci_jugador,
            pp.id_equipo,
            j.nombre,
            j.apellido
        FROM planilla_partido pp
        JOIN jugador j ON j.ci = pp.ci_jugador
        WHERE pp.id_partido = %s
        ORDER BY pp.id_equipo, j.apellido, j.nombre
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_partido,))
        return cursor.fetchall()


def obtener(conn, id_partido, ci_jugador):
    sql = """
        SELECT *
        FROM planilla_partido
        WHERE id_partido = %s
          AND ci_jugador = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_partido, ci_jugador))
        return cursor.fetchone()


def insertar(conn, id_partido, ci_jugador, id_equipo):
    sql = """
        INSERT INTO planilla_partido (
            id_partido,
            ci_jugador,
            id_equipo
        )
        VALUES (%s, %s, %s)
    """

    with conn.cursor() as cursor:
        cursor.execute(
            sql,
            (id_partido, ci_jugador, id_equipo)
        )


def eliminar_no_incluidos(conn, id_partido, ci_jugadores):
    """
    Elimina de la planilla los jugadores que ya no aparecen
    en la lista enviada.
    """
    if not ci_jugadores:
        sql = """
            DELETE FROM planilla_partido
            WHERE id_partido = %s
        """
        params = (id_partido,)

    else:
        placeholders = ", ".join(["%s"] * len(ci_jugadores))

        sql = f"""
            DELETE FROM planilla_partido
            WHERE id_partido = %s
              AND ci_jugador NOT IN ({placeholders})
        """

        params = [id_partido] + ci_jugadores

    with conn.cursor() as cursor:
        cursor.execute(sql, params)


def tiene_registros_asociados(conn, id_partido, ci_jugador):
    """
    Comprueba si el jugador ya tiene goles o tarjetas
    registrados en este partido.
    """
    sql = """
        SELECT
            EXISTS (
                SELECT 1
                FROM gol
                WHERE id_partido = %s
                  AND ci_jugador = %s
            )
            OR EXISTS (
                SELECT 1
                FROM tarjeta
                WHERE id_partido = %s
                  AND ci_jugador = %s
            ) AS tiene_registros
    """

    with conn.cursor() as cursor:
        cursor.execute(
            sql,
            (
                id_partido,
                ci_jugador,
                id_partido,
                ci_jugador
            )
        )

        return bool(cursor.fetchone()["tiene_registros"])