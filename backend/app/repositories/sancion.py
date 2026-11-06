def listar(conn, id_torneo=None, ci_jugador=None):
    sql = """
        SELECT
            s.*,
            j.nombre,
            j.apellido,
            t.nombre AS nombre_torneo
        FROM sancion_jugador s
        JOIN jugador j ON j.ci = s.ci_jugador
        JOIN torneo t ON t.id_torneo = s.id_torneo
        WHERE 1 = 1
    """

    params = []

    if id_torneo is not None:
        sql += " AND s.id_torneo = %s"
        params.append(id_torneo)

    if ci_jugador is not None:
        sql += " AND s.ci_jugador = %s"
        params.append(ci_jugador)

    sql += """
        ORDER BY
            s.id_torneo,
            s.numero_fecha_inicio,
            j.apellido,
            j.nombre
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()


def obtener(conn, id_sancion):
    sql = """
        SELECT
            s.*,
            j.nombre,
            j.apellido,
            t.nombre AS nombre_torneo
        FROM sancion_jugador s
        JOIN jugador j ON j.ci = s.ci_jugador
        JOIN torneo t ON t.id_torneo = s.id_torneo
        WHERE s.id_sancion = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_sancion,))
        return cursor.fetchone()


def bloquear(conn, id_sancion):
    sql = """
        SELECT *
        FROM sancion_jugador
        WHERE id_sancion = %s
        FOR UPDATE
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_sancion,))
        return cursor.fetchone()


def jugador_inscripto_en_torneo(conn, ci_jugador, id_torneo):
    """
    Comprueba que el jugador forme parte de un equipo
    de la edición indicada.
    """
    sql = """
        SELECT ej.ci_jugador
        FROM equipo_jugador_torneo ej
        JOIN equipo e ON e.id_equipo = ej.id_equipo
        WHERE ej.ci_jugador = %s
          AND e.id_torneo = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (ci_jugador, id_torneo))
        return cursor.fetchone()


def crear(conn, datos):
    sql = """
        INSERT INTO sancion_jugador (
            ci_jugador,
            id_torneo,
            motivo,
            numero_fecha_inicio,
            cantidad_fechas
        )
        VALUES (%s, %s, %s, %s, %s)
    """

    valores = (
        datos.ci_jugador,
        datos.id_torneo,
        datos.motivo,
        datos.numero_fecha_inicio,
        datos.cantidad_fechas
    )

    with conn.cursor() as cursor:
        cursor.execute(sql, valores)
        return cursor.lastrowid


def actualizar(conn, id_sancion, datos):
    sql = """
        UPDATE sancion_jugador
        SET motivo = %s,
            numero_fecha_inicio = %s,
            cantidad_fechas = %s
        WHERE id_sancion = %s
    """

    valores = (
        datos.motivo,
        datos.numero_fecha_inicio,
        datos.cantidad_fechas,
        id_sancion
    )

    with conn.cursor() as cursor:
        cursor.execute(sql, valores)


def eliminar(conn, id_sancion):
    sql = """
        DELETE FROM sancion_jugador
        WHERE id_sancion = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, (id_sancion,))

def esta_suspendido(
    conn,
    ci_jugador,
    id_torneo,
    numero_fecha
):
    sql = """
        SELECT EXISTS (
            SELECT 1
            FROM sancion_jugador
            WHERE ci_jugador = %s
              AND id_torneo = %s
              AND numero_fecha_inicio <= %s
              AND %s < numero_fecha_inicio + cantidad_fechas
        ) AS suspendido
    """

    with conn.cursor() as cursor:
        cursor.execute(
            sql,
            (
                ci_jugador,
                id_torneo,
                numero_fecha,
                numero_fecha
            )
        )

        return cursor.fetchone()["suspendido"]