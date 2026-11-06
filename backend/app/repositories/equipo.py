_SELECT = """
    SELECT e.id_equipo, e.nombre, e.id_torneo, t.nombre AS torneo, t.estado AS estado_torneo,
           e.id_facultad, f.nombre AS facultad, e.ci_capitan,
           CONCAT(j.nombre, ' ', j.apellido) AS capitan,
           COUNT(ejt.ci_jugador) AS cantidad_jugadores
      FROM equipo e
      JOIN torneo t ON t.id_torneo = e.id_torneo
      JOIN facultad f ON f.id_facultad = e.id_facultad
 LEFT JOIN jugador j ON j.ci = e.ci_capitan
 LEFT JOIN equipo_jugador_torneo ejt ON ejt.id_equipo = e.id_equipo
"""


def listar(conn, id_torneo: int | None = None, id_facultad: int | None = None, q: str | None = None):
    condiciones, params = [], []
    if id_torneo is not None:
        condiciones.append("e.id_torneo = %s")
        params.append(id_torneo)
    if id_facultad is not None:
        condiciones.append("e.id_facultad = %s")
        params.append(id_facultad)
    if q:
        condiciones.append("e.nombre LIKE %s")
        params.append(f"%{q}%")

    sql = _SELECT
    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)
    sql += " GROUP BY e.id_equipo ORDER BY e.nombre"

    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def obtener(conn, id_equipo: int):
    with conn.cursor() as cur:
        cur.execute(_SELECT + " WHERE e.id_equipo = %s GROUP BY e.id_equipo", (id_equipo,))
        return cur.fetchone()


def plantel(conn, id_equipo: int):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT j.ci, j.nombre, j.apellido, j.tipo, j.id_facultad, ejt.numero_camiseta,
                   (j.ci <=> e.ci_capitan) AS es_capitan
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
            SELECT e.id_equipo, e.id_torneo, e.id_facultad, e.ci_capitan,
                   t.estado AS estado_torneo
              FROM equipo e
              JOIN torneo t ON t.id_torneo = e.id_torneo
             WHERE e.id_equipo = %s
             FOR UPDATE OF e
            """,
            (id_equipo,),
        )
        return cur.fetchone()


def torneo_estado(conn, id_torneo: int):
    """Obtiene el estado y ID del torneo para validaciones de negocio en servicios."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id_torneo, estado FROM torneo WHERE id_torneo = %s",
            (id_torneo,),
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