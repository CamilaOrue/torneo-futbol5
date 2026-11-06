def obtener_partido(conn, id_partido):
    sql = """
        SELECT
            p.id_partido,
            p.id_torneo,
            p.numero_fecha,
            p.id_equipo_local,
            p.id_equipo_visitante,
            p.dia,
            p.estado,
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


def listar(conn, id_partido):
    sql = """
        SELECT
            t.id_tarjeta,
            t.id_partido,
            t.ci_jugador,
            t.minuto,
            t.color,
            j.nombre,
            j.apellido
        FROM tarjeta t
        JOIN jugador j ON j.ci = t.ci_jugador
        WHERE t.id_partido = %s
        ORDER BY t.minuto, t.id_tarjeta
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_partido,))
        return cursor.fetchall()


def obtener(conn, id_tarjeta):
    sql = """
        SELECT *
        FROM tarjeta
        WHERE id_tarjeta = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_tarjeta,))
        return cursor.fetchone()


def jugador_en_planilla(conn, id_partido, ci_jugador):
    sql = """
        SELECT id_equipo
        FROM planilla_partido
        WHERE id_partido = %s
          AND ci_jugador = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_partido, ci_jugador))
        return cursor.fetchone()


def contar_amarillas_edicion(conn, ci_jugador, id_torneo):
    sql = """
        SELECT COUNT(*) AS cantidad
        FROM tarjeta t
        JOIN partido p ON p.id_partido = t.id_partido
        WHERE t.ci_jugador = %s
          AND p.id_torneo = %s
          AND t.color = 'amarilla'
          AND p.estado <> 'cancelado'
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (ci_jugador, id_torneo))
        return cursor.fetchone()["cantidad"]


def insertar(conn, id_partido, datos):
    sql = """
        INSERT INTO tarjeta (
            id_partido,
            ci_jugador,
            minuto,
            color
        )
        VALUES (%s, %s, %s, %s)
    """

    with conn.cursor() as cursor:
        cursor.execute(
            sql,
            (
                id_partido,
                datos.ci_jugador,
                datos.minuto,
                datos.color
            )
        )

        return cursor.lastrowid


def crear_sancion_automatica(
    conn,
    ci_jugador,
    id_torneo,
    motivo,
    numero_fecha_inicio,
    id_tarjeta_origen
):
    sql = """
        INSERT INTO sancion_jugador (
            ci_jugador,
            id_torneo,
            motivo,
            numero_fecha_inicio,
            cantidad_fechas,
            id_tarjeta_origen
        )
        VALUES (%s, %s, %s, %s, 1, %s)
    """

    with conn.cursor() as cursor:
        cursor.execute(
            sql,
            (
                ci_jugador,
                id_torneo,
                motivo,
                numero_fecha_inicio,
                id_tarjeta_origen
            )
        )


def sancion_por_tarjeta(conn, id_tarjeta):
    sql = """
        SELECT id_sancion
        FROM sancion_jugador
        WHERE id_tarjeta_origen = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_tarjeta,))
        return cursor.fetchone()


def actualizar(conn, id_tarjeta, datos):
    sql = """
        UPDATE tarjeta
        SET minuto = %s
        WHERE id_tarjeta = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(
            sql,
            (datos.minuto, id_tarjeta)
        )


def eliminar(conn, id_tarjeta):
    sql = """
        DELETE FROM tarjeta
        WHERE id_tarjeta = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_tarjeta,))


def tiene_sancion_automatica_en_edicion(conn, ci_jugador, id_torneo):
    sql = """
        SELECT id_sancion
        FROM sancion_jugador
        WHERE ci_jugador = %s
          AND id_torneo = %s
          AND id_tarjeta_origen IS NOT NULL
        LIMIT 1
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (ci_jugador, id_torneo))
        return cursor.fetchone()