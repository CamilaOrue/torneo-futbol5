
# verifica que cierto jugador relmente forme parte de uno de los dos equipos

def equipo_del_jugador(conn, ci, id_equipo_local, id_equipo_visitante):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id_equipo
            FROM equipo_jugador_torneo
            WHERE ci_jugador = %s
            AND id_equipo IN (%s, %s)
            """,
            (ci, id_equipo_local, id_equipo_visitante,)
        )
        fila = cur.fetchone()
        return fila["id_equipo"] if fila else None  # id del equipo, o None si no es de ninguno


# verifica que un jugador esté en una planilla

def esta_en_planilla(conn, id_partido, ci):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 1
            FROM planilla_partido
            WHERE id_partido = %s
            AND ci_jugador = %s
            LIMIT 1
            """,
            (id_partido, ci,)
        )
        return cur.fetchone() is not None


# consulta la cantidad de amarillas de un jugador dado

def cantidad_amarillas(conn, ci, id_torneo):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS cantidad
            FROM tarjeta t
            JOIN partido p ON t.id_partido = p.id_partido
            WHERE t.ci_jugador = %s
            AND p.id_torneo = %s
            AND t.color = 'amarilla'
            """,
            (ci, id_torneo,)
        )
        return cur.fetchone()["cantidad"]


# verifica si un jugador tiene una sancion

def esta_suspendido(conn, ci, id_torneo, numero_fecha):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS cantidad
            FROM sancion_jugador
            WHERE %s BETWEEN numero_fecha_inicio
                        AND numero_fecha_inicio + cantidad_fechas - 1
            AND ci_jugador = %s
            AND id_torneo = %s
            """, 
            (numero_fecha, ci, id_torneo,)
        )
        return cur.fetchone()["cantidad"] > 0

    

# inserta planilla en la bdd

def insertar_en_planilla(conn, id_partido, ci, id_equipo):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO planilla_partido (id_partido, ci_jugador, id_equipo)
            VALUES (%s, %s, %s)
            """, 
            (id_partido, ci, id_equipo)
        )


# insertar gol en la bdd

def insertar_gol(conn, id_partido, ci, minuto, autogol):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO gol (id_partido, ci_jugador, minuto, autogol)
            VALUES (%s, %s, %s, %s)
            """, 
            (id_partido, ci, minuto, autogol)
        )
        return cur.lastrowid


# insertar tarjeta en la bdd

def insertar_tarjeta(conn, id_partido, ci, minuto, color):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO tarjeta (id_partido, ci_jugador, minuto, color)
            VALUES (%s, %s, %s, %s)
            """, 
            (id_partido, ci, minuto, color)
        )
        return cur.lastrowid


# insertar sancion en la bdd

def insertar_sancion(conn, ci, id_torneo, motivo, numero_fecha_inicio):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO sancion_jugador
                (ci_jugador, id_torneo, motivo, numero_fecha_inicio)
            VALUES (%s, %s, %s, %s)
            """, 
            (ci, id_torneo, motivo, numero_fecha_inicio)
        )


def obtener_gol(conn, id_gol):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM gol
            WHERE id_gol = %s
            """,
            (id_gol,)
        )
        fila = cur.fetchone()


def quitar_gol(conn, id_gol):
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM gol
            WHERE id_gol = %s
            """,
            (id_gol,)
        )


    