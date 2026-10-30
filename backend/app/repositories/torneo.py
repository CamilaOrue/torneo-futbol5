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
