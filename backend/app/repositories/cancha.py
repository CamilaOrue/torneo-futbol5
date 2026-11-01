
def listar(conn, id_complejo: int | None = None):
    sql = """
        SELECT nombre_cancha, id_complejo, superficie, techada
        FROM cancha
    """
    params = []

    if id_complejo is not None:
        sql += " WHERE id_complejo = %s"
        params.append(id_complejo)

    sql += " ORDER BY id_complejo, nombre_cancha"

    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def obtener(conn, id_complejo: int, nombre_cancha: str):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT nombre_cancha, id_complejo, superficie, techada
            FROM cancha
            WHERE id_complejo = %s
              AND nombre_cancha = %s
        """, (id_complejo, nombre_cancha))
        return cur.fetchone()


def crear(conn, datos: dict):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO cancha
                    (nombre_cancha, id_complejo, superficie, techada)
                VALUES (%s, %s, %s, %s)
            """, (
                datos["nombre_cancha"],
                datos["id_complejo"],
                datos["superficie"],
                datos["techada"]
            ))

        conn.commit()
        return obtener(
            conn,
            datos["id_complejo"],
            datos["nombre_cancha"]
        )

    except Exception:
        conn.rollback()
        raise


def modificar(
    conn,
    id_complejo: int,
    nombre_cancha: str,
    datos: dict
):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE cancha
                SET superficie = %s,
                    techada = %s
                WHERE id_complejo = %s
                  AND nombre_cancha = %s
            """, (
                datos["superficie"],
                datos["techada"],
                id_complejo,
                nombre_cancha
            ))

        conn.commit()
        return obtener(conn, id_complejo, nombre_cancha)

    except Exception:
        conn.rollback()
        raise


def eliminar(conn, id_complejo: int, nombre_cancha: str):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM cancha
                WHERE id_complejo = %s
                  AND nombre_cancha = %s
            """, (id_complejo, nombre_cancha))

            eliminado = cur.rowcount > 0

        conn.commit()
        return eliminado

    except Exception:
        conn.rollback()
        raise
