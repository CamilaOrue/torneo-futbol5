def obtener_equipo(conn, id_equipo: int):
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


def obtener_jugador(conn, ci: str):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT ci, id_facultad, tipo
              FROM jugador
             WHERE ci = %s
             FOR UPDATE
            """,
            (ci,),
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


def listar(conn, id_equipo: int):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT j.ci, j.nombre, j.apellido, j.tipo, ejt.numero_camiseta, (j.ci = e.ci_capitan) AS es_capitan
              FROM equipo_jugador_torneo ejt
              JOIN equipo e ON e.id_equipo = ejt.id_equipo
              JOIN jugador j ON j.ci = ejt.ci_jugador
             WHERE ejt.id_equipo = %s
             ORDER BY ejt.numero_camiseta
            """,
            (id_equipo,),
        )
        return cur.fetchall()


def cantidad(conn, id_equipo: int) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS total
              FROM equipo_jugador_torneo
             WHERE id_equipo = %s
            """,
            (id_equipo,),
        )
        return cur.fetchone()["total"]


def cantidad_externos(conn, id_equipo: int) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS total
              FROM equipo_jugador_torneo ejt
              JOIN jugador j ON j.ci = ejt.ci_jugador
             WHERE ejt.id_equipo = %s
               AND j.tipo IN ('docente', 'funcionario')
            """,
            (id_equipo,),
        )
        return cur.fetchone()["total"]


def agregar(conn, id_equipo: int, ci: str, id_torneo: int, numero_camiseta: int):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO equipo_jugador_torneo
                (id_equipo, ci_jugador, id_torneo, numero_camiseta)
            VALUES (%s, %s, %s, %s)
            """,
            (id_equipo, ci, id_torneo, numero_camiseta),
        )


def actualizar_camiseta(
    conn, id_equipo: int, ci: str, numero_camiseta: int
):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE equipo_jugador_torneo
               SET numero_camiseta = %s
             WHERE id_equipo = %s AND ci_jugador = %s
            """,
            (numero_camiseta, id_equipo, ci),
        )


def eliminar(conn, id_equipo: int, ci: str):
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM equipo_jugador_torneo
             WHERE id_equipo = %s AND ci_jugador = %s
            """,
            (id_equipo, ci),
        )


def es_capitan(conn, id_equipo: int, ci: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 1
              FROM equipo
             WHERE id_equipo = %s AND ci_capitan = %s
            """,
            (id_equipo, ci),
        )
        return cur.fetchone() is not None

#ver
def jugadores_en_otro_equipo(conn, cis, id_torneo, id_equipo):
    if not cis:
        return []

    placeholders = ", ".join(["%s"] * len(cis))

    sql = f"""
        SELECT ci_jugador
        FROM equipo_jugador_torneo
        WHERE ci_jugador IN ({placeholders})
          AND id_torneo = %s
          AND id_equipo <> %s
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (*cis, id_torneo, id_equipo))
        return cursor.fetchall()


def bloquear_equipo(conn, id_equipo):
    sql = """
        SELECT id_equipo
        FROM equipo
        WHERE id_equipo = %s
        FOR UPDATE
    """
    with conn.cursor() as cursor:
        cursor.execute(sql, (id_equipo,))
        return cursor.fetchone()
