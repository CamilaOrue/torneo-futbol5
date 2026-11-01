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


# ---------------------------------------------------------------- escritura
def existe_facultad(conn, id_facultad: int) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM facultad WHERE id_facultad = %s", (id_facultad,))
        return cur.fetchone() is not None


def bloquear(conn, ci: str):
    """Lee el jugador bloqueando la fila hasta el commit (evita carreras en la modificación)."""
    with conn.cursor() as cur:
        cur.execute("SELECT ci, id_facultad, tipo FROM jugador WHERE ci = %s FOR UPDATE", (ci,))
        return cur.fetchone()


def crear(conn, d: dict):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO jugador (ci, nombre, apellido, email, fecha_nacimiento, id_facultad, tipo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (d["ci"], d["nombre"], d["apellido"], d["email"],
             d["fecha_nacimiento"], d["id_facultad"], d["tipo"]),
        )


def actualizar(conn, ci: str, d: dict):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE jugador
               SET nombre = %s, apellido = %s, email = %s,
                   fecha_nacimiento = %s, id_facultad = %s, tipo = %s
             WHERE ci = %s
            """,
            (d["nombre"], d["apellido"], d["email"],
             d["fecha_nacimiento"], d["id_facultad"], d["tipo"], ci),
        )


def eliminar(conn, ci: str):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM jugador WHERE ci = %s", (ci,))


# ---------------------------------------------------------------- reglas de plantel
def planteles_de_otra_facultad(conn, ci: str, id_facultad: int) -> list[str]:
    """Equipos en cuyo plantel está el jugador y que NO representan a `id_facultad`."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT e.nombre
              FROM equipo_jugador_torneo ejt
              JOIN equipo e ON e.id_equipo = ejt.id_equipo
             WHERE ejt.ci_jugador = %s AND e.id_facultad <> %s
            """,
            (ci, id_facultad),
        )
        return [r["nombre"] for r in cur.fetchall()]


def planteles_sin_cupo_externo(conn, ci: str) -> list[str]:
    """Equipos del jugador que ya tienen 2 docentes/funcionarios además de él."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT e.nombre
              FROM equipo_jugador_torneo ejt
              JOIN equipo e ON e.id_equipo = ejt.id_equipo
             WHERE ejt.ci_jugador = %s
               AND (SELECT COUNT(*)
                      FROM equipo_jugador_torneo x
                      JOIN jugador jx ON jx.ci = x.ci_jugador
                     WHERE x.id_equipo = ejt.id_equipo
                       AND x.ci_jugador <> ejt.ci_jugador
                       AND jx.tipo IN ('docente', 'funcionario')) >= 2
            """,
            (ci,),
        )
        return [r["nombre"] for r in cur.fetchall()]
