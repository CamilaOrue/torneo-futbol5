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
            g.id_gol,
            g.id_partido,
            g.ci_jugador,
            g.minuto,
            g.autogol,
            j.nombre,
            j.apellido,
            ej.id_equipo AS equipo_jugador,
            CASE
                WHEN g.autogol = TRUE
                    THEN CASE
                        WHEN ej.id_equipo = p.id_equipo_local
                            THEN p.id_equipo_visitante
                        ELSE p.id_equipo_local
                    END
                ELSE ej.id_equipo
            END AS equipo_que_suma_gol
        FROM gol g
        JOIN partido p
            ON p.id_partido = g.id_partido
        JOIN planilla_partido pp
            ON pp.id_partido = g.id_partido
           AND pp.ci_jugador = g.ci_jugador
        JOIN equipo_jugador_torneo ej
            ON ej.id_equipo = pp.id_equipo
           AND ej.ci_jugador = pp.ci_jugador
        JOIN jugador j
            ON j.ci = g.ci_jugador
        WHERE g.id_partido = %s
        ORDER BY g.minuto, g.id_gol
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_partido,))
        return cursor.fetchall()


def obtener(conn, id_gol):
    sql = """
        SELECT
            id_gol,
            id_partido,
            ci_jugador,
            minuto,
            autogol
        FROM gol
        WHERE id_gol = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_gol,))
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


def insertar(conn, id_partido, datos):
    sql = """
        INSERT INTO gol (
            id_partido,
            ci_jugador,
            minuto,
            autogol
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
                datos.autogol
            )
        )

        return cursor.lastrowid


def actualizar(conn, id_gol, datos):
    sql = """
        UPDATE gol
        SET ci_jugador = %s,
            minuto = %s,
            autogol = %s
        WHERE id_gol = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(
            sql,
            (
                datos.ci_jugador,
                datos.minuto,
                datos.autogol,
                id_gol
            )
        )


def eliminar(conn, id_gol):
    sql = """
        DELETE FROM gol
        WHERE id_gol = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_gol,))


def resultado(conn, id_partido):
    sql = """
        SELECT
            p.id_equipo_local,
            p.id_equipo_visitante,

            COALESCE(SUM(
                CASE
                    WHEN
                        CASE
                            WHEN g.autogol = TRUE THEN
                                CASE
                                    WHEN pp.id_equipo = p.id_equipo_local
                                        THEN p.id_equipo_visitante
                                    ELSE p.id_equipo_local
                                END
                            ELSE pp.id_equipo
                        END = p.id_equipo_local
                    THEN 1
                    ELSE 0
                END
            ), 0) AS goles_local,

            COALESCE(SUM(
                CASE
                    WHEN
                        CASE
                            WHEN g.autogol = TRUE THEN
                                CASE
                                    WHEN pp.id_equipo = p.id_equipo_local
                                        THEN p.id_equipo_visitante
                                    ELSE p.id_equipo_local
                                END
                            ELSE pp.id_equipo
                        END = p.id_equipo_visitante
                    THEN 1
                    ELSE 0
                END
            ), 0) AS goles_visitante

        FROM partido p
        LEFT JOIN gol g
            ON g.id_partido = p.id_partido
        LEFT JOIN planilla_partido pp
            ON pp.id_partido = g.id_partido
           AND pp.ci_jugador = g.ci_jugador
        WHERE p.id_partido = %s
        GROUP BY
            p.id_partido,
            p.id_equipo_local,
            p.id_equipo_visitante
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_partido,))
        return cursor.fetchone()