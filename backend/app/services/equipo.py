from app.repositories import equipo as repo


# Verifica que el equipo cumpla las reglas del plantel.
# No retorna nada: si alguna regla no se cumple, lanza un ValueError.
def equipo_valido(conn, id_equipo):
    equipo = repo.obtener(conn, id_equipo)
    if equipo is None:
        raise ValueError("El equipo no existe")

    plantel = repo.plantel(conn, id_equipo)

    if not tiene_entre_5_y_10_jugadores(plantel):
        raise ValueError("El equipo debe tener entre 5 y 10 jugadores")

    if not maximo_dos_funcionarios(plantel):
        raise ValueError("El equipo debe tener como máximo 2 funcionarios")

    if not todos_pertenecen_a_misma_facultad(plantel, equipo["id_facultad"]):
        raise ValueError("Todos los jugadores deben pertenecer a la misma facultad que el equipo")


def tiene_entre_5_y_10_jugadores(plantel):
    return 5 <= len(plantel) <= 10


# Docentes y funcionarios cuentan juntos para el máximo de 2.
def maximo_dos_funcionarios(plantel):
    num_funcionarios = sum(1 for jugador in plantel if jugador["tipo"] in ("funcionario", "docente"))
    return num_funcionarios <= 2


def todos_pertenecen_a_misma_facultad(plantel, id_facultad_equipo):
    return all(jugador["id_facultad"] == id_facultad_equipo for jugador in plantel)
