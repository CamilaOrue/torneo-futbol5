_SELECT = """
    SELECT t.id_torneo, t.nombre, t.anio, t.semestre, t.fecha_inicio, t.fecha_fin, t.estado,
           (SELECT COUNT(*) FROM equipo e WHERE e.id_torneo = t.id_torneo) AS cantidad_equipos,
           (SELECT COUNT(*) FROM partido p WHERE p.id_torneo = t.id_torneo) AS cantidad_partidos,
           (SELECT COUNT(*) FROM partido p
             WHERE p.id_torneo = t.id_torneo AND p.estado = 'jugado') AS partidos_jugados
      FROM torneo t
"""


def listar(conn):
    with conn.cursor() as cur:
        cur.execute(_SELECT + " ORDER BY t.anio DESC, t.semestre DESC")
        return cur.fetchall()


def obtener(conn, id_torneo: int):
    with conn.cursor() as cur:
        cur.execute(_SELECT + " WHERE t.id_torneo = %s", (id_torneo,))
        return cur.fetchone()


def insertar_torneo(conn, datos):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO torneo (
                nombre, anio, semestre, fecha_inicio, fecha_fin
            )
            VALUES (%s, %s, %s, %s, %s)
            """, 
            (datos.nombre, datos.anio, datos.semestre, datos.fecha_inicio, datos.fecha_fin )
        )
        return cur.lastrowid


def existe_edicion(conn, anio, semestre):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 1
            FROM torneo
            WHERE anio = %s AND semestre = %s
            LIMIT 1
        """, (anio, semestre))
        return cur.fetchone() is not None


def actualizar_estado(conn, id_torneo, estado):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE torneo
            SET estado = %s
            WHERE id_torneo = %s
        """, (estado, id_torneo))