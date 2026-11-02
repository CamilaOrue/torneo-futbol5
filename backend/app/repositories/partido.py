#las reglas las aplica service, no estas consultas


# consulta para verificar que no se repita rival, si dos equipos ya tienen un partido 
# no cancelado en el torneo
# retorna true/false

def ya_se_enfrentaron (conn, id_torneo, equipo_a, equipo_b, excluir_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            Select Count(*) as enfrentamiento
            from partido 
            where 
            
                ((id_equipo_local = %s and id_equipo_visitante = %s)  
                or (id_equipo_local = %s and id_equipo_visitante = %s))
                and id_partido <> %s
                and estado <> 'cancelado'
                and id_torneo = %s
            """,
            (equipo_a, equipo_b, equipo_b, equipo_a, excluir_id, id_torneo,),
        )
        return cur.fetchone()["enfrentamiento"] > 0


# consulta que verifica si un equipo no tiene mas de un partido asignado por fecha
# retorna true/false

def equipo_juega_en_fecha (conn, id_torneo, numero_fecha, id_equipo, excluir_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            Select Count(*) as en_fecha
            from partido 
            where 
                (id_equipo_local = %s or id_equipo_visitante = %s)  
                and id_partido <> %s
                and estado <> 'cancelado'
                and id_torneo = %s
                and numero_fecha = %s
            """,
            (id_equipo, id_equipo, excluir_id, id_torneo, numero_fecha,),
        )
        return cur.fetchone()["en_fecha"] > 0


# consulta para verifiar que np exista más de un partido el mismo dia en una misma cancha
# retorna true/false

def cancha_ocupada (conn, dia, id_turno, nombre_cancha, id_complejo, excluir_id):
    with conn.cursor() as cur:
        cur.execute(
            """ 
            Select Count(*) as ocupada
            from partido
            where dia = %s
            and id_turno = %s
            and nombre_cancha = %s
            and id_complejo = %s
            and id_partido <> %s
            and ocupa_cancha =1
            """,
            (dia, id_turno, nombre_cancha, id_complejo, excluir_id,),
        )
        return cur.fetchone()["ocupada"] > 0


#cantidad de jugadores en un equipo sean minimo 5
# retorna un numero entero

def num_jugadores_equipo(conn, id_equipo):
    with conn.cursor() as cur:
        cur.execute(
            """
            Select Count(*) as cantidad_jugadores
            from equipo_jugador_torneo
            where id_equipo = %s
            """,
            (id_equipo,),
        )
        return cur.fetchone()["cantidad_jugadores"] #numero de jugadores dle plantel


#consulta en que estdo se escuentra cierto torneo
#retorna txto

def estado_torneo(conn, id_torneo):
    with conn.cursor() as cur:
        cur.execute(
            """
            Select estado
            from torneo
            where id_torneo = %s
            """,
            (id_torneo,),
        )
        fila = cur.fetchone()
        return fila["estado"] if fila else None # el estado, o None si no existe
    

# a cual torneo pertenece cierto equipo
# retorna un numero entero

def torneo_del_equipo(conn, id_equipo):
    with conn.cursor() as cur:
        cur.execute(
            """
            Select id_torneo
            from equipo
            where id_equipo = %s
            """,
            (id_equipo,),
        )
        fila = cur.fetchone()
        return fila["id_torneo"] if fila else None  # el id del torneo, o None si no existe


# obtiene los datos de un partido
# retorna un diccionario con todas las columnas de partido más hora_fin
# ejemplo partido["estado"], partido["dia"], partido["hora_fin"]

def obtener_info_partido(conn, id_partido):
    with conn.cursor() as cur:
        cur.execute(
            """
            Select partido.*, turno.hora_fin
            from partido
            join turno on partido.id_turno = turno.id_turno
            where id_partido = %s
            """,
            (id_partido,),
        )
        return cur.fetchone()  # diccionario con los datos del partido, o None si no existe