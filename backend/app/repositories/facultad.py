def listar(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id_facultad, nombre FROM facultad ORDER BY nombre")
        return cur.fetchall()
