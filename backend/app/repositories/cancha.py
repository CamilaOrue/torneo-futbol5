def listar(conn, id_complejo: int):
    sql = """
        SELECT nombre_cancha, id_complejo, superficie, techada
        FROM cancha
        WHERE id_complejo = %s
        ORDER BY nombre_cancha
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_complejo,))
        return cursor.fetchall()


def obtener(conn, id_complejo: int, nombre_cancha: str):
    sql = """
        SELECT c.nombre_cancha, c.id_complejo, comp.nombre AS nombre_complejo, c.superficie, c.techada
          FROM cancha c
          JOIN complejo comp ON comp.id_complejo = c.id_complejo
         WHERE c.id_complejo = %s AND c.nombre_cancha = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_complejo, nombre_cancha))
        return cursor.fetchone()


def crear(conn, id_complejo: int, datos: dict):
    sql = """
        INSERT INTO cancha (nombre_cancha, id_complejo, superficie, techada)
        VALUES (%s, %s, %s, %s)
    """

    with conn.cursor() as cursor:
        cursor.execute(
            sql, (datos["nombre_cancha"], id_complejo, datos["superficie"], datos["techada"])
        )


def actualizar(conn, id_complejo: int, nombre_cancha: str, datos: dict):
    sql = """
        UPDATE cancha
        SET
            superficie = %s, techada = %s
        WHERE id_complejo = %s AND nombre_cancha = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(
            sql, (datos["superficie"], datos["techada"], id_complejo, nombre_cancha)
        )


def eliminar(conn, id_complejo: int, nombre_cancha: str):
    sql = """
        DELETE FROM cancha
        WHERE id_complejo = %s
          AND nombre_cancha = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_complejo, nombre_cancha))