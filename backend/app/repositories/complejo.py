def listar(conn, q=None):
    sql = """
        SELECT c.id_complejo, c.nombre, c.direccion, c.departamento, COUNT(can.nombre_cancha) AS cantidad_canchas
        FROM complejo c
        LEFT JOIN cancha can
            ON can.id_complejo = c.id_complejo
    """
    
    params = []
    if q:
        sql += " WHERE c.nombre LIKE %s OR c.departamento LIKE %s"
        patron = f"%{q}%"
        params.extend([patron, patron])
        
    sql += """
        GROUP BY c.id_complejo, c.nombre, c.direccion, c.departamento
        ORDER BY c.nombre
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()


def obtener(conn, id_complejo: int):
    sql = """
        SELECT
            id_complejo, nombre, direccion, departamento
        FROM complejo
        WHERE id_complejo = %s
    """
    with conn.cursor() as cursor:
        cursor.execute(sql, (id_complejo,))
        return cursor.fetchone()


def crear(conn, datos: dict):
    sql = """
        INSERT INTO complejo (nombre, direccion, departamento) 
        VALUES (%s, %s, %s)
    """
    with conn.cursor() as cursor:
        cursor.execute(
            sql, (datos["nombre"], datos["direccion"], datos["departamento"])
        )
        return cursor.lastrowid


def actualizar(conn, id_complejo: int, datos: dict):
    sql = """
        UPDATE complejo
        SET nombre = %s, direccion = %s, departamento = %s
        WHERE id_complejo = %s
    """
    with conn.cursor() as cursor:
        cursor.execute(
            sql, (datos["nombre"], datos["direccion"], datos["departamento"], id_complejo)
        )


def eliminar(conn, id_complejo: int):
    sql = """
        DELETE FROM complejo
        WHERE id_complejo = %s
    """
    with conn.cursor() as cursor:
        cursor.execute(sql, (id_complejo,))


def bloquear(conn, id_complejo: int):
    sql = """
        SELECT id_complejo, nombre
        FROM complejo
        WHERE id_complejo = %s
        FOR UPDATE
    """
    with conn.cursor() as cur:
        cur.execute(sql, (id_complejo,))
        return cur.fetchone()