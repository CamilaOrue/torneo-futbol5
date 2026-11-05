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
            SELECT j.ci, j.nombre, j.apellido, j.tipo, j.id_facultad, ejt.numero_camiseta,
                   (j.ci = e.ci_capitan) AS es_capitan
              FROM equipo_jugador_torneo ejt
              JOIN equipo  e ON e.id_equipo = ejt.id_equipo
              JOIN jugador j ON j.ci = ejt.ci_jugador
             WHERE ejt.id_equipo = %s
             ORDER BY ejt.numero_camiseta
            """,
            (id_equipo,),
        )
        return cur.fetchall()

def bloquear(conn, id_equipo: int):
    """Bloquea el equipo durante la transacción."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id_equipo, id_torneo, id_facultad, ci_capitan
              FROM equipo
             WHERE id_equipo = %s
             FOR UPDATE
            """,
            (id_equipo,),
        )
        return cur.fetchone()


def torneo_en_inscripcion(conn, id_torneo: int) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT estado FROM torneo WHERE id_torneo = %s",
            (id_torneo,),
        )
        torneo = cur.fetchone()
        return torneo is not None and torneo["estado"] == "inscripcion"


def existe_facultad(conn, id_facultad: int) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM facultad WHERE id_facultad = %s",
            (id_facultad,),
        )
        return cur.fetchone() is not None


def existe_capitan_en_plantel(conn, id_equipo: int, ci: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 1
              FROM equipo_jugador_torneo
             WHERE id_equipo = %s AND ci_jugador = %s
            """,
            (id_equipo, ci),
        )
        return cur.fetchone() is not None


def crear(conn, d: dict):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO equipo (nombre, id_torneo, id_facultad)
            VALUES (%s, %s, %s)
            """,
            (d["nombre"], d["id_torneo"], d["id_facultad"]),
        )
        return cur.lastrowid


def actualizar(conn, id_equipo: int, d: dict):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE equipo
               SET nombre = %s, id_facultad = %s
             WHERE id_equipo = %s
            """,
            (d["nombre"], d["id_facultad"], id_equipo),
        )


def asignar_capitan(conn, id_equipo: int, ci: str):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE equipo
               SET ci_capitan = %s
             WHERE id_equipo = %s
            """,
            (ci, id_equipo),
        )


def eliminar(conn, id_equipo: int):
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM equipo WHERE id_equipo = %s",
            (id_equipo,),
        )
