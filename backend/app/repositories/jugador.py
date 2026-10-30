_SELECT = """
    SELECT j.ci, j.nombre, j.apellido, j.email, j.fecha_nacimiento,
           j.id_facultad, f.nombre AS facultad, j.tipo,
           (SELECT e.nombre
              FROM equipo_jugador_torneo ejt
              JOIN equipo e ON e.id_equipo = ejt.id_equipo
              JOIN torneo t ON t.id_torneo = ejt.id_torneo
             WHERE ejt.ci_jugador = j.ci
             ORDER BY t.anio DESC, t.semestre DESC
             LIMIT 1) AS equipo_actual
      FROM jugador j
      JOIN facultad f ON f.id_facultad = j.id_facultad
"""


def _like(texto: str) -> str:
    """Escapa los comodines de LIKE para que el texto se busque literal."""
    escapado = texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escapado}%"


def listar(conn, q: str | None = None, id_facultad: int | None = None, tipo: str | None = None):
    # Solo se concatenan fragmentos fijos; todos los valores van como parámetros.
    condiciones, params = [], []
    if q:
        condiciones.append(
            "(j.nombre LIKE %s OR j.apellido LIKE %s OR j.ci LIKE %s OR j.email LIKE %s"
            " OR CONCAT(j.nombre, ' ', j.apellido) LIKE %s)"
        )
        params += [_like(q)] * 5
    if id_facultad is not None:
        condiciones.append("j.id_facultad = %s")
        params.append(id_facultad)
    if tipo is not None:
        condiciones.append("j.tipo = %s")
        params.append(tipo)

    sql = _SELECT
    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)
    sql += " ORDER BY j.apellido, j.nombre"
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def obtener(conn, ci: str):
    with conn.cursor() as cur:
        cur.execute(_SELECT + " WHERE j.ci = %s", (ci,))
        return cur.fetchone()


def equipos_de(conn, ci: str):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT e.id_equipo, e.nombre AS equipo, t.id_torneo, t.nombre AS torneo,
                   ejt.numero_camiseta
              FROM equipo_jugador_torneo ejt
              JOIN equipo e ON e.id_equipo = ejt.id_equipo
              JOIN torneo t ON t.id_torneo = ejt.id_torneo
             WHERE ejt.ci_jugador = %s
             ORDER BY t.anio DESC, t.semestre DESC
            """,
            (ci,),
        )
        return cur.fetchall()
