_SELECT = """
    SELECT e.id_equipo, e.nombre, e.id_torneo, t.nombre AS torneo,
           e.id_facultad, f.nombre AS facultad,
           e.ci_capitan, CONCAT(c.nombre, ' ', c.apellido) AS capitan,
           (SELECT COUNT(*) FROM equipo_jugador_torneo ejt
             WHERE ejt.id_equipo = e.id_equipo) AS cantidad_jugadores
      FROM equipo e
      JOIN torneo   t ON t.id_torneo   = e.id_torneo
      JOIN facultad f ON f.id_facultad = e.id_facultad
      LEFT JOIN jugador c ON c.ci = e.ci_capitan
"""


def listar(conn, id_torneo: int | None = None):
    sql, params = _SELECT, []
    if id_torneo is not None:
        sql += " WHERE e.id_torneo = %s"
        params.append(id_torneo)
    sql += " ORDER BY t.anio DESC, t.semestre DESC, e.nombre"
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def obtener(conn, id_equipo: int):
    with conn.cursor() as cur:
        cur.execute(_SELECT + " WHERE e.id_equipo = %s", (id_equipo,))
        return cur.fetchone()


def plantel(conn, id_equipo: int):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT j.ci, j.nombre, j.apellido, j.tipo, ejt.numero_camiseta,
                   (j.ci = e.ci_capitan) AS es_capitan
              FROM equipo_jugador_torneo ejt
              JOIN equipo  e ON e.id_equipo = ejt.id_equipo
              JOIN jugador j ON j.ci        = ejt.ci_jugador
             WHERE ejt.id_equipo = %s
             ORDER BY ejt.numero_camiseta
            """,
            (id_equipo,),
        )
        return cur.fetchall()
