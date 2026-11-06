def resultados_del_torneo(conn, id_torneo):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT partido.id_equipo_local, partido.id_equipo_visitante,
                SUM(CASE WHEN (planilla_partido.id_equipo = partido.id_equipo_local AND gol.autogol = FALSE)
                        OR (planilla_partido.id_equipo = partido.id_equipo_visitante AND gol.autogol = TRUE)
                        THEN 1 ELSE 0 END) AS goles_local,
                SUM(CASE WHEN (planilla_partido.id_equipo = partido.id_equipo_visitante AND gol.autogol = FALSE)
                        OR (planilla_partido.id_equipo = partido.id_equipo_local AND gol.autogol = TRUE)
                        THEN 1 ELSE 0 END) AS goles_visitante
                from partido
                left join gol on partido.id_partido = gol.id_partido
                left join planilla_partido on gol.id_partido = planilla_partido.id_partido and gol.ci_jugador = planilla_partido.ci_jugador
                where partido.id_torneo = %s AND partido.estado='jugado'
                Group By partido.id_partido, partido.id_equipo_local, partido.id_equipo_visitante
            """,
            (id_torneo,)
        )
        return cur.fetchall()    

# consulta para buscar los id d elos equipos y su snombres q se utiliza para armarr la tabla de resultados en los reportes
def equipos_del_torneo(conn, id_torneo):
    with conn.cursor as cur:
        cur.execute(
            """
            SELECT id_equipo, nombre
            FROM equipo 
            WHERE id_torneo = %s
            """,
            (id_torneo,)
        )
        return cur.fetchall()


def jugadores_por_facultad_y_tipo(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(jugador.ci) as cantidad_jugador, 
                facultad.nombre as nombre_facultad, jugador.tipo as tipo_jugador
            FROM jugador
            JOIN facultad on jugador.id_facultad = facultad.id_facultad
            GROUP BY facultad.id_facultad, jugador.tipo
            ORDER BY facultad.nombre, jugador.tipo
            """
        )
        return cur.fetchall()

def porcentaje_de_partidos_por_estado(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT partido.estado, COUNT(*) as cantidad, 
                ROUND(COUNT(*) / (SELECT COUNT(*) FROM partido) *100 , 1) AS porcentaje
            FROM partido
            GROUP BY partido.estado;
            """
        )
        return cur.fetchall()


def cantidad_sanciones_por_eq_motivo(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT equipo.nombre as equipo, sancion_jugador.motivo, COUNT(*) AS cantidad_sanciones
            FROM sancion_jugador
            JOIN equipo_jugador_torneo on sancion_jugador.ci_jugador = equipo_jugador_torneo.ci_jugador
                and sancion_jugador.id_torneo  = equipo_jugador_torneo.id_torneo
            JOIN equipo on equipo_jugador_torneo.id_equipo = equipo.id_equipo
            GROUP BY equipo.id_equipo, equipo.nombre, sancion_jugador.motivo
            ORDER BY equipo.nombre, sancion_jugador.motivo
            """
        )
        return cur.fetchall()

def canchas_mas_usadas(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT cancha.nombre_cancha, complejo.nombre as complejo_nombre, COUNT(*) as cantidad_usos
            FROM partido
            JOIN cancha on partido.nombre_cancha = cancha.nombre_cancha and partido.id_complejo = cancha.id_complejo
            JOIN complejo on cancha.id_complejo = complejo.id_complejo
            GROUP BY cancha.nombre_cancha, cancha.id_complejo
            ORDER BY cantidad_usos DESC
            """
        )
        return cur.fetchall()


# MySQL devuelve las columnas TIME como duraciones, que FastAPI envía en segundos
# (por ejemplo, 72000 en lugar de 20:00). Por eso se formatean en el SQL con
# TIME_FORMAT, para que lleguen como texto "HH:MM".
def turnos_mas_usados(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 
                turno.id_turno, 
                TIME_FORMAT(turno.hora_inicio, '%H:%i') AS hora_inicio,
                TIME_FORMAT(turno.hora_fin,    '%H:%i') AS hora_fin, 
                COUNT(*) as turno_mas_utilizados

            FROM partido
            JOIN turno on partido.id_turno = turno.id_turno
            GROUP BY turno.id_turno
            ORDER BY turno_mas_utilizados DESC
            """
        )
        return cur.fetchall()

def top_diez_jugadores(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT jugador.nombre, jugador.apellido, COUNT(*) as cantidad_goles
            FROM gol
            JOIN jugador on gol.ci_jugador = jugador.ci
            WHERE gol.autogol = FALSE
            GROUP BY gol.ci_jugador
            ORDER BY cantidad_goles DESC
            LIMIT 10
            """
        )
        return cur.fetchall()


def jugadores_no_en_planilla(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT jugador.nombre as jugador_nombre, jugador.apellido as jugador_apellido, equipo.nombre as equipo_nombre
            from equipo_jugador_torneo
            JOIN jugador on equipo_jugador_torneo.ci_jugador = jugador.ci
            JOIN equipo on equipo_jugador_torneo.id_equipo = equipo.id_equipo and equipo_jugador_torneo.id_torneo = equipo.id_torneo
            LEFT JOIN planilla_partido on equipo_jugador_torneo.ci_jugador = planilla_partido.ci_jugador
            WHERE planilla_partido.ci_jugador IS NULL
            """
        )
        return cur.fetchall() 


def tabla_fair_play(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT equipo.nombre AS equipo,
                SUM(CASE WHEN tarjeta.color = 'amarilla' THEN 1 ELSE 0 END) AS amarillas,
                SUM(CASE WHEN tarjeta.color = 'roja'     THEN 1 ELSE 0 END) AS rojas,
                SUM(CASE WHEN tarjeta.color = 'amarilla' THEN 1
                            WHEN tarjeta.color = 'roja'     THEN 3
                            ELSE 0 END) AS puntos
            FROM equipo
            LEFT JOIN planilla_partido
                ON planilla_partido.id_equipo = equipo.id_equipo
            LEFT JOIN tarjeta
                ON tarjeta.id_partido = planilla_partido.id_partido
                AND tarjeta.ci_jugador = planilla_partido.ci_jugador
            WHERE equipo.id_torneo = 1
            GROUP BY equipo.id_equipo, equipo.nombre
            ORDER BY puntos ASC, equipo.nombre
            """
        )
        return cur.fetchall()


def promedio_goles_por_partido_fecha(conn, id_torneo):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT goles_partido.numero_fecha,
                COUNT(*) AS partidos_jugados,
                SUM(goles_partido.goles) AS goles,
                ROUND(AVG(goles_partido.goles), 2) AS promedio_goles
            FROM (SELECT partido.id_partido, partido.numero_fecha, COUNT(gol.id_gol) AS goles
                FROM partido
                LEFT JOIN gol ON gol.id_partido = partido.id_partido
                WHERE partido.id_torneo = %s AND partido.estado = 'jugado'
                GROUP BY partido.id_partido, partido.numero_fecha) AS goles_partido
            GROUP BY goles_partido.numero_fecha
            ORDER BY goles_partido.numero_fecha
            """,
            (id_torneo,),
        )
        return cur.fetchall() 

def promedio_goles_por_partido_edicion(conn, id_torneo):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS partidos_jugados,
                SUM(goles_partido.goles) AS goles,
                ROUND(AVG(goles_partido.goles), 2) AS promedio_goles
            FROM (SELECT partido.id_partido, COUNT(gol.id_gol) AS goles
                FROM partido
                LEFT JOIN gol ON gol.id_partido = partido.id_partido
                WHERE partido.id_torneo = %s AND partido.estado = 'jugado'
                GROUP BY partido.id_partido) AS goles_partido
            """,
            (id_torneo,),
        )
        return cur.fetchall() 


