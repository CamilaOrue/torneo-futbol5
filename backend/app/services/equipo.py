import pymysql
from fastapi import HTTPException

from app.repositories import equipo as repo
from app.repositories import plantel as repo_plantel


def _traducir(e: pymysql.MySQLError):
    codigo = e.args[0] if e.args else None

    if codigo == 1062:
        raise HTTPException(
            409, "Ya existe un equipo con ese nombre en esta edición del torneo."
        )

    if codigo == 1452:
        raise HTTPException(
            404, "El torneo o la facultad indicada no existe."
        )

    if codigo in (1451, 1217):
        raise HTTPException(
            409, "No se puede eliminar el equipo porque tiene partidos asociados."
        )

    raise e


# ---------------------------------------------------------------- reglas de negocio
def validar_plantel_completo(conn, id_equipo: int):
    """
    Verifica que el equipo cumpla con todas las reglas de integración del plantel antes de permitir
    que dispute un partido (entre 5 y 10 jugadores, máx 2 docentes/funcionarios, misma facultad).
    """
    equipo = repo.obtener(conn, id_equipo)
    if not equipo:
        raise HTTPException(404, "El equipo no existe.")

    plantel = repo.plantel(conn, id_equipo)

    # 1. Cantidad de jugadores (entre 5 y 10)
    if not (5 <= len(plantel) <= 10):
        raise HTTPException(
            400, f"El equipo '{equipo['nombre']}' debe tener entre 5 y 10 jugadores (actualmente tiene {len(plantel)})."
        )

    # 2. Máximo 2 docentes/funcionarios
    num_externos = sum(1 for j in plantel if j["tipo"] in ("docente", "funcionario"))
    if num_externos > 2:
        raise HTTPException(
            400, f"El equipo '{equipo['nombre']}' supera el cupo máximo de 2 docentes/funcionarios (tiene {num_externos})."
        )

    # 3. Todos los jugadores deben pertenecer a la misma facultad del equipo
    fuera_de_facultad = [j for j in plantel if j.get("id_facultad") != equipo["id_facultad"]]
    if fuera_de_facultad:
        raise HTTPException(
            400, f"Todos los jugadores del equipo '{equipo['nombre']}' deben pertenecer a la facultad del equipo."
        )


# ---------------------------------------------------------------- OPERACIONES CRUD
def listar(conn, id_torneo: int | None = None, id_facultad: int | None = None, q: str | None = None):
    return repo.listar(conn, id_torneo, id_facultad, q.strip() if q else None)


def obtener(conn, id_equipo: int):
    equipo = repo.obtener(conn, id_equipo)
    if not equipo:
        raise HTTPException(404, "No se encontró el equipo.")
    equipo["plantel"] = repo.plantel(conn, id_equipo)
    return equipo


def crear(conn, datos):
    try:
        torneo = repo.torneo_estado(conn, datos.id_torneo)
        if not torneo:
            raise HTTPException(404, "No se encontró el torneo indicado.")

        # Regla: Los equipos solo se crean en etapa de inscripción
        if torneo["estado"] != "inscripcion":
            raise HTTPException(
                400, "Solo se pueden registrar equipos en torneos que estén en etapa de inscripción."
            )

        if not repo.existe_facultad(conn, datos.id_facultad):
            raise HTTPException(404, "No se encontró la facultad indicada.")

        id_creado = repo.crear(conn, datos.model_dump())
        resultado = repo.obtener(conn, id_creado)

        conn.commit()
        return resultado

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)


def actualizar(conn, id_equipo: int, datos):
    try:
        equipo_actual = repo.bloquear(conn, id_equipo)
        if not equipo_actual:
            raise HTTPException(404, "No se encontró el equipo.")

        if equipo_actual["estado_torneo"] != "inscripcion":
            raise HTTPException(
                400, "Solo se pueden modificar equipos cuando el torneo está en etapa de inscripción."
            )

        if not repo.existe_facultad(conn, datos.id_facultad):
            raise HTTPException(404, "No se encontró la facultad indicada.")

        # Los jugadores deben ser de la facultad del equipo: no se cambia si ya tiene plantel
        if datos.id_facultad != equipo_actual["id_facultad"] and repo.plantel(conn, id_equipo):
            raise HTTPException(
                400, "No se puede cambiar la facultad de un equipo que ya tiene jugadores en su plantel."
            )

        # Si se especifica un capitán, debe pertenecer al plantel del equipo
        if datos.ci_capitan and not repo.existe_capitan_en_plantel(conn, id_equipo, datos.ci_capitan):
            raise HTTPException(
                400, "El capitán asignado debe ser un jugador que integre el plantel del equipo."
            )

        repo.actualizar(conn, id_equipo, datos.model_dump())
        if datos.ci_capitan:
            repo.asignar_capitan(conn, id_equipo, datos.ci_capitan)
        resultado = repo.obtener(conn, id_equipo)

        conn.commit()
        return resultado

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)


def eliminar(conn, id_equipo: int):
    try:
        equipo_actual = repo.bloquear(conn, id_equipo)
        if not equipo_actual:
            raise HTTPException(404, "No se encontró el equipo.")

        if equipo_actual["estado_torneo"] != "inscripcion":
            raise HTTPException(
                400, "Solo se pueden eliminar equipos mientras el torneo esté en etapa de inscripción."
            )

        # En inscripción el plantel es solo la lista de inscriptos: se borra junto con el equipo.
        # Si el equipo ya tiene partidos, la FK lo impide y se informa con _traducir.
        repo_plantel.eliminar_integrantes(conn, id_equipo)
        repo.eliminar(conn, id_equipo)
        conn.commit()

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)
