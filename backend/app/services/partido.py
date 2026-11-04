from app.repositories import partido as repo
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

ZONA_HORARIA = ZoneInfo("America/Montevideo")


# cambios permitidos al modificar el estado de un partido 

CAMBIOS_PERMITIDOS = {
    "programado": ["jugado", "postergado", "cancelado"],
    "postergado": ["cancelado"],
    "jugado": [],
    "cancelado": [],
}




# Fecha y hora actual en Uruguay (el contenedor usa UTC, 3 horas adelantado)
# Retorna: un datetime sin zona horaria, comparable con los datos de la base.
def ahora():
    return datetime.now(ZONA_HORARIA).replace(tzinfo=None)

# Momento en que termina un partido: su día más la hora de fin de su turno.
# Retorna: un datetime (por ejemplo 10/11/2026 19:00).
def fin_del_partido(partido):
    return datetime.combine(partido["dia"], datetime.min.time()) + partido["hora_fin"]


# Verifica que el partido no esté jugado.
# No retorna nada: si el partido está jugado, lanza un error y corta la operación.

def verificar_no_jugado(partido): #debe de haber una consulta previa a la bdd antes de usar
    if partido["estado"] == "jugado":
        raise ValueError("El partido ya se jugó: no se puede modificar ni eliminar")


#verificar si un partido existe, si no existe lanza un error
def verificar_existe(partido):
    if partido is None:
        raise ValueError("El partido no existe")


#verificar la cantidad minima de jugadores
def verificar_minimo_jugadores(conn, id_equipo):
    num_jugadores = repo.num_jugadores_equipo(conn, id_equipo)

    if (num_jugadores < 5 ):
        raise ValueError(f"El equipo tiene {num_jugadores} jugadores y necesita al menos 5 para jugar")

    

def verificar_rivales_no_repetidos(conn, id_torneo, equipo_a, equipo_b, excluir_id):
    ya_jugaron = repo.ya_se_enfrentaron(conn, id_torneo, equipo_a, equipo_b, excluir_id)
    if (ya_jugaron):
        raise ValueError("Los equipos tienen más de un partido (no cancelado) en la edicion")


def verificar_fecha_libre(conn, id_torneo, numero_fecha, id_equipo, excluir_id):
    fecha_ocupada = repo.equipo_juega_en_fecha(conn, id_torneo, numero_fecha, id_equipo, excluir_id)
    if (fecha_ocupada):
        raise ValueError(f"El equipo {id_equipo} ya tiene un partido en la fecha {numero_fecha}")

def verificar_cancha_libre(conn, dia, id_turno, nombre_cancha, id_complejo, excluir_id):
    cancha_ocupada = repo.cancha_ocupada(conn, dia, id_turno, nombre_cancha, id_complejo, excluir_id)
    if (cancha_ocupada):
        raise ValueError("Ya existe un partido activo en la cancha en ese horario")


def verificar_estado_torneo(conn, id_torneo):
    estado = repo.estado_torneo(conn, id_torneo)
    if (estado is None): raise ValueError("El torneo no existe")

    if (estado != "en curso"): raise ValueError("El torneo no se encuentra en curso")


def verificar_equipos(conn, id_torneo, equipo_local, equipo_visitante):

    if (equipo_local == equipo_visitante): raise ValueError("Local y visitante son el mismo equipo")

    torneo_local = repo.torneo_del_equipo(conn, equipo_local)
    torneo_vis = repo.torneo_del_equipo(conn, equipo_visitante)

    if(torneo_local is None): raise ValueError("El equipo local no existe")
    if(torneo_vis is None): raise ValueError("El equipo visitante no existe")

    if (torneo_local != id_torneo): raise ValueError("El equipo local no pertenece a este torneo")
    if (torneo_vis != id_torneo): raise ValueError("El equipo visitante no pertenece a este torneo")


# Verifica que el partido no esté cancelado.
# No retorna nada: si el partido está cancelado, lanza un error y corta la operación.
def verificar_no_cancelado(partido): 
    if (partido["estado"] == "cancelado"):
        raise ValueError("El partido está cancelado: para volver a jugarlo hay que crear uno nuevo")


# saber si ya termino elpartidopara maracarlo como jugado
def verificar_ya_paso(partido):
    if(ahora() < fin_del_partido(partido)):
        raise ValueError("El partido todavía no se jugó: no se puede marcar como jugado")
    

# si ya pasan mas de 48 horas, no sepuede odificr unnpartido jugado
def verificar_48_horas(partido):
    if (ahora() - fin_del_partido(partido) > timedelta(hours=48)):
        raise ValueError("Pasaron más de 48 horas desde el partido: el resultado ya no se puede corregir")


# verifica segun el estado actual del partido, a cuales estados puede pasar
def verificar_cambio_valido(partido, nuevo_estado):
    permitido_actual = CAMBIOS_PERMITIDOS[partido["estado"]]

    if(nuevo_estado not in permitido_actual):
        raise ValueError(f"No se puede pasar un partido de {partido['estado']} a {nuevo_estado}")

# ----------------------------- Funciones que utilizan las verificaciones ----------------------------------


# Crea un partido nuevo, verificando todas las reglas de la letra antes de guardarlo.
# Si alguna regla no se cumple, lanza un ValueError y no guarda nada.
def crear_partido(conn, datos):

    # 1. El torneo existe y está en curso
    verificar_estado_torneo(conn, datos["id_torneo"])

    # 2. Local y visitante son distintos, existen y son de este torneo
    verificar_equipos(conn, datos["id_torneo"], datos["id_equipo_local"], datos["id_equipo_visitante"])

    # 3. Cada equipo tiene al menos 5 jugadores
    verificar_minimo_jugadores(conn, datos["id_equipo_local"])
    verificar_minimo_jugadores(conn, datos["id_equipo_visitante"])

    # 4. Los equipos no se enfrentaron antes en esta edición (salvo cancelado)
    #    0 = partido nuevo, no hay que excluir ninguno
    verificar_rivales_no_repetidos(conn, datos["id_torneo"], datos["id_equipo_local"], datos["id_equipo_visitante"], 0)

    # 5. Ninguno de los dos equipos juega otro partido en esta fecha
    verificar_fecha_libre(conn, datos["id_torneo"], datos["numero_fecha"], datos["id_equipo_local"], 0)
    verificar_fecha_libre(conn, datos["id_torneo"], datos["numero_fecha"], datos["id_equipo_visitante"], 0)

    # 6. La cancha está libre ese día y turno
    verificar_cancha_libre(conn, datos["dia"], datos["id_turno"], datos["nombre_cancha"], datos["id_complejo"], 0)

    # 7. Pasó todas las verificaciones: guardar el partido
    return repo.insertar_partido(conn, datos)


# el router solo sabe el id por lo que hay q buscar todo el partido en la bdd
def eliminar_partido(conn, id_partido):

    # 1. Consultar el partido (una sola vez)
    partido = repo.obtener_info_partido(conn, id_partido)

    verificar_existe(partido)
    verificar_estado_torneo(conn, partido["id_torneo"]) # el torneo tiene que estar en curso
    verificar_no_jugado(partido) # un partido ya jugado no se puede eliminar

    return repo.quitar_partido(conn, id_partido)


# Si el partido estaba postergado, vuelve a quedar programado.
def modificar_partido(conn, id_partido, datos):
    # 1. Consultar el partido (una sola vez)
    partido = repo.obtener_info_partido(conn, id_partido)

    # 2. Verificaciones del partido actual
    verificar_existe(partido)                              # primero: si no existe, lo demás fallaría
    verificar_estado_torneo(conn, partido["id_torneo"])    # el torneo tiene que estar en curso
    verificar_no_jugado(partido)                           # un partido jugado no se modifica
    verificar_no_cancelado(partido)                        # un cancelado es definitivo: se crea uno nuevo

    # 3. El lugar nuevo tiene que estar libre (sin contar a este mismo partido)
    verificar_cancha_libre(conn, datos["dia"], datos["id_turno"], datos["nombre_cancha"], datos["id_complejo"], id_partido)

    # 4. Pasó todas las verificaciones: guardar los cambios
    repo.actualizar_partido(conn, id_partido, datos)


def cambiar_estado(conn, id_partido, nuevo_estado):

    partido = repo.obtener_info_partido(conn, id_partido)
    verificar_existe(partido)                              
    verificar_estado_torneo(conn, partido["id_torneo"])
    verificar_cambio_valido(partido, nuevo_estado)

    if (nuevo_estado == 'jugado'):
        verificar_ya_paso(partido)

    repo.actualizar_estado(conn, id_partido, nuevo_estado)


# resultado de un partido dado segun goles del local y del visitante.
# retorna un diccionario con id_equipo_local, id_equipo_visitante, goles_local y goles_visitante.
def resultado(conn, id_partido):
    partido = repo.obtener_info_partido(conn, id_partido)
    verificar_existe(partido)
    return repo.goles_del_partido(conn, id_partido)
