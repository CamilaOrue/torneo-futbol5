import pymysql

def listar(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id_complejo, nombre, direccion, departamento
            FROM complejo
            ORDER BY nombre
        """)
        return cur.fetchall()


def obtener(conn, id_complejo: int):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id_complejo, nombre, direccion, departamento
            FROM complejo
            WHERE id_complejo = %s
        """, (id_complejo,))
        return cur.fetchone()


def crear(conn, datos: dict):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO complejo (nombre, direccion, departamento)
                VALUES (%s, %s, %s)
            """, (
                datos["nombre"],
                datos["direccion"],
                datos["departamento"]
            ))
            id_complejo = cur.lastrowid

        conn.commit()
        return obtener(conn, id_complejo)

    except Exception:
        conn.rollback()
        raise


def modificar(conn, id_complejo: int, datos: dict):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE complejo
                SET nombre = %s,
                    direccion = %s,
                    departamento = %s
                WHERE id_complejo = %s
            """, (
                datos["nombre"],
                datos["direccion"],
                datos["departamento"],
                id_complejo
            ))

        conn.commit()
        return obtener(conn, id_complejo)

    except Exception:
        conn.rollback()
        raise


def eliminar(conn, id_complejo: int):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM complejo
                WHERE id_complejo = %s
            """, (id_complejo,))

            eliminado = cur.rowcount > 0

        conn.commit()
        return eliminado

    except Exception:
        conn.rollback()
        raise
