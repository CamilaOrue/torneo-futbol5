from app.repositories import planilla as repo
from app.repositories import partido as repo_partido
from app.services import partido as servicio_partido


# funcion reutilizable para saber si un partido es apto para ser registrado en una planilla

def verificar_partido_registrable(partido):

    servicio_partido.verificar_existe(partido) # ya tiene el error en els service de partido

    if(partido["estado"] != "jugado"): raise ValueError ("El partido aun no se ha jugado")

    servicio_partido.verificar_48_horas(partido)


#regla para guardar una planilla

def guardar_planilla(conn, id_partido, jugadores): # jugadores es una lista de cedulas

    partido = repo_partido.obtener_info_partido(conn, id_partido)

    verificar_partido_registrable(partido)

    for ci in jugadores:

        id_equipo = repo.equipo_del_jugador(
            conn,
            ci,
            partido["id_equipo_local"],
            partido["id_equipo_visitante"]
        )

        if (id_equipo is None):
            raise ValueError (f"El jugador {ci} no pertenece a ninguno de los dos equipos")

        suspendido = repo.esta_suspendido(
            conn,
            ci,
            partido["id_torneo"],
            partido["numero_fecha"]
        )

        if suspendido:
            raise ValueError(f"El jugador {ci} está suspendido")

        if (repo.esta_en_planilla(conn, id_partido, ci)):
            raise ValueError (f"El jugador {ci} ya está en la planilla")


        repo.insertar_en_planilla(
            conn,
            id_partido,
            ci,
            id_equipo
        )



# regla para insertar un gol

def registrar_gol(conn, id_partido, ci, minuto, autogol):

    partido = repo_partido.obtener_info_partido(conn, id_partido)

    verificar_partido_registrable(partido)

    if not repo.esta_en_planilla(conn, id_partido, ci):
        raise ValueError(f"El jugador {ci} no está en la planilla del partido")

    return repo.insertar_gol(conn, id_partido, ci, minuto, autogol)


# regla para insertar las tarjetas

def registrar_tarjeta(conn, id_partido, ci, minuto, color):

    partido = repo_partido.obtener_info_partido(conn, id_partido)

    verificar_partido_registrable(partido)

    if not repo.esta_en_planilla(conn, id_partido, ci):
        raise ValueError(f"El jugador {ci} no está en la planilla del partido")

    id_tarjeta = repo.insertar_tarjeta(conn, id_partido, ci, minuto, color)

    if color == "roja":
        repo.insertar_sancion(
            conn,
            ci,
            partido["id_torneo"],
            "roja",
            partido["numero_fecha"] + 1
        )

    elif color == "amarilla":
        cantidad = repo.cantidad_amarillas(
            conn,
            ci,
            partido["id_torneo"]
        )

        if cantidad % 3 == 0:
            repo.insertar_sancion(
                conn,
                ci,
                partido["id_torneo"],
                "acumulacion_amarillas",
                partido["numero_fecha"] + 1
            )

    return id_tarjeta


def eliminar_gol(conn, id_gol):
    gol = repo.obtener_gol(conn, id_gol)

    if gol is None: 
        raise ValueError("El gol a eliminar no existe")
    
    partido = repo_partido.obtener_info_partido(conn, gol["id_partido"])
    verificar_partido_registrable(partido)
    repo.quitar_gol(conn, id_gol)

