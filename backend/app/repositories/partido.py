def listar(conn, id_torneo=None, numero_fecha=None, estado=None):
    sql = """
        SELECT p.*, t.hora_inicio, t.hora_fin
        FROM partido p
        JOIN turno t ON t.id_turno = p.id_turno
        WHERE 1 = 1
    """
    params = []

    if id_torneo is not None:
        sql += " AND p.id_torneo = %s"
        params.append(id_torneo)

    if numero_fecha is not None:
        sql += " AND p.numero_fecha = %s"
        params.append(numero_fecha)

    if estado is not None:
        sql += " AND p.estado = %s"
        params.append(estado)

    sql += " ORDER BY p.dia, t.hora_inicio"

    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()


def obtener(conn, id_partido):
    sql = """
        SELECT p.*, t.hora_inicio, t.hora_fin
        FROM partido p
        JOIN turno t ON t.id_turno = p.id_turno
        WHERE p.id_partido = %s
    """
    with conn.cursor() as cursor:
        cursor.execute(sql, (id_partido,))
        return cursor.fetchone()


def bloquear_torneo(conn, id_torneo):
    sql = """
        SELECT id_torneo, estado
        FROM torneo
        WHERE id_torneo = %s
        FOR UPDATE
    """
    with conn.cursor() as cursor:
        cursor.execute(sql, (id_torneo,))
        return cursor.fetchone()


def obtener_equipo(conn, id_equipo, id_torneo):
    sql = """
        SELECT id_equipo
        FROM equipo
        WHERE id_equipo = %s
          AND id_torneo = %s
    """
    with conn.cursor() as cursor:
        cursor.execute(sql, (id_equipo, id_torneo))
        return cursor.fetchone()


def contar_jugadores(conn, id_equipo):
    sql = """
        SELECT COUNT(*) AS cantidad
        FROM equipo_jugador_torneo
        WHERE id_equipo = %s
    """
    with conn.cursor() as cursor:
        cursor.execute(sql, (id_equipo,))
        return cursor.fetchone()["cantidad"]


def existe_turno(conn, id_turno):
    sql = """
        SELECT id_turno
        FROM turno
        WHERE id_turno = %s
    """
    with conn.cursor() as cursor:
        cursor.execute(sql, (id_turno,))
        return cursor.fetchone()


def existe_cancha(conn, nombre_cancha, id_complejo):
    sql = """
        SELECT nombre_cancha
        FROM cancha
        WHERE nombre_cancha = %s
          AND id_complejo = %s
    """
    with conn.cursor() as cursor:
        cursor.execute(sql, (nombre_cancha, id_complejo))
        return cursor.fetchone()


def enfrentamiento_existente(conn, id_torneo, id_equipo_local, id_equipo_visitante, excluir=None):
    sql = """
        SELECT id_partido
        FROM partido
        WHERE id_torneo = %s
          AND estado <> 'cancelado'
          AND (
                (id_equipo_local = %s AND id_equipo_visitante = %s)
             OR (id_equipo_local = %s AND id_equipo_visitante = %s)
          )
    """
    params = [
        id_torneo,
        id_equipo_local,
        id_equipo_visitante,
        id_equipo_visitante,
        id_equipo_local
    ]
    if excluir is not None:
        sql += " AND id_partido <> %s"
        params.append(excluir)

    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchone()


def equipo_ya_juega_en_fecha(conn, id_equipo, id_torneo, numero_fecha, excluir=None):
    sql = """
        SELECT id_partido
        FROM partido
        WHERE id_torneo = %s
          AND numero_fecha = %s
          AND estado <> 'cancelado'
          AND (
                id_equipo_local = %s
             OR id_equipo_visitante = %s
          )
    """
    params = [id_torneo, numero_fecha, id_equipo, id_equipo]
    if excluir is not None:
        sql += " AND id_partido <> %s"
        params.append(excluir)

    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchone()


def cancha_ocupada(conn, dia, id_turno, nombre_cancha, id_complejo, excluir=None):
    sql = """
        SELECT id_partido
        FROM partido
        WHERE dia = %s
          AND id_turno = %s
          AND nombre_cancha = %s
          AND id_complejo = %s
    """
    params = [dia, id_turno, nombre_cancha, id_complejo]
    if excluir is not None:
        sql += " AND id_partido <> %s"
        params.append(excluir)

    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchone()


def crear(conn, datos):
    sql = """
        INSERT INTO partido (
            id_torneo,
            numero_fecha,
            id_equipo_local,
            id_equipo_visitante,
            dia,
            id_turno,
            nombre_cancha,
            id_complejo,
            estado
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'programado')
    """
    valores = (
        datos.id_torneo,
        datos.numero_fecha,
        datos.id_equipo_local,
        datos.id_equipo_visitante,
        datos.dia,
        datos.id_turno,
        datos.nombre_cancha,
        datos.id_complejo
    )
    with conn.cursor() as cursor:
        cursor.execute(sql, valores)
        return cursor.lastrowid


def bloquear_partido(conn, id_partido):
    sql = """
        SELECT p.*, t.hora_inicio, t.hora_fin
        FROM partido p
        JOIN turno t ON t.id_turno = p.id_turno
        WHERE p.id_partido = %s
        FOR UPDATE
    """
    with conn.cursor() as cursor:
        cursor.execute(sql, (id_partido,))
        return cursor.fetchone()


def actualizar_programacion(conn, id_partido, datos):
    sql = """
        UPDATE partido
        SET numero_fecha = %s,
            dia = %s,
            id_turno = %s,
            nombre_cancha = %s,
            id_complejo = %s
        WHERE id_partido = %s
    """
    valores = (
        datos.numero_fecha,
        datos.dia,
        datos.id_turno,
        datos.nombre_cancha,
        datos.id_complejo,
        id_partido
    )
    with conn.cursor() as cursor:
        cursor.execute(sql, valores)


def actualizar_estado(conn, id_partido, estado):
    sql = "UPDATE partido SET estado = %s WHERE id_partido = %s"
    with conn.cursor() as cursor:
        cursor.execute(sql, (estado, id_partido))


def eliminar(conn, id_partido):
    sql = "DELETE FROM partido WHERE id_partido = %s"
    with conn.cursor() as cursor:
        cursor.execute(sql, (id_partido,))


def goles_del_partido(conn, id_partido):
    sql = """
        SELECT COUNT(*) as goles_local, 
               (SELECT COUNT(*) FROM gol WHERE id_partido = %s AND id_equipo_a_favor != p.id_equipo_local) as goles_visitante
        FROM gol g
        JOIN partido p ON p.id_partido = g.id_partido
        WHERE g.id_partido = %s AND g.id_equipo_a_favor = p.id_equipo_local
    """
    with conn.cursor() as cur:
        cur.execute(sql, (id_partido, id_partido))
        return cur.fetchone() or {"goles_local": 0, "goles_visitante": 0}
    
