import pymysql
from fastapi import HTTPException

from app.repositories import plantel as repo


def _traducir(e):
    codigo = e.args[0] if e.args else None

    if codigo == 1062:
        raise HTTPException(
            409,
            "Uno de los jugadores ya está inscripto en otro equipo o hay datos duplicados"
        )

    if codigo in (1451, 1217):
        raise HTTPException(
            409,
            "No se puede modificar el plantel porque existen registros asociados"
        )

    if codigo == 1452:
        raise HTTPException(
            404,
            "No se encontró uno de los jugadores o el equipo"
        )

    raise e


def listar(conn, id_equipo):
    equipo = repo.obtener_equipo(conn, id_equipo)
    if not equipo:
        raise HTTPException(404, "No se encontró el equipo")

    return {
        "id_equipo": id_equipo,
        "integrantes": repo.listar(conn, id_equipo),
        "ci_capitan": equipo["ci_capitan"]
    }


def actualizar(conn, id_equipo, datos):
    try:
        equipo = repo.obtener_equipo(conn, id_equipo)
        if not equipo:
            raise HTTPException(404, "No se encontró el equipo")

        if not repo.bloquear_equipo(conn, id_equipo):
            raise HTTPException(404, "No se encontró el equipo")

        if not repo.torneo_en_inscripcion(conn, equipo["id_torneo"]):
            raise HTTPException(
                409,
                "El plantel solamente puede modificarse durante la inscripción"
            )

        integrantes = datos.integrantes
        cis = [i.ci_jugador for i in integrantes]

        # El capitán debe formar parte del plantel
        if datos.ci_capitan not in cis:
            raise HTTPException(
                400,
                "El capitán debe ser uno de los integrantes del plantel"
            )

        jugadores = repo.obtener_jugadores(conn, cis)

        # Comprobamos que existan todos los jugadores
        if len(jugadores) != len(cis):
            raise HTTPException(
                404,
                "Uno o más jugadores no existen"
            )

        # Todos deben pertenecer a la facultad del equipo
        if any(j["id_facultad"] != equipo["id_facultad"] for j in jugadores):
            raise HTTPException(
                400,
                "Todos los jugadores deben pertenecer a la facultad del equipo"
            )

        # Máximo dos docentes y funcionarios combinados
        cantidad_docentes = sum(
            1 for j in jugadores
            if j["tipo"] in ("docente", "funcionario")
        )

        if cantidad_docentes > 2:
            raise HTTPException(
                400,
                "El plantel admite como máximo dos docentes y funcionarios"
            )

        # Un jugador no puede estar en otro equipo de la misma edición
        repetidos = repo.jugadores_en_otro_equipo(
            conn, cis, equipo["id_torneo"], id_equipo
        )

        if repetidos:
            raise HTTPException(
                409,
                "Uno o más jugadores ya pertenecen a otro equipo de esta edición"
            )

        # Reemplazamos el plantel
        repo.eliminar_integrantes(conn, id_equipo)

        for integrante in integrantes:
            repo.insertar_integrante(
                conn,
                id_equipo,
                integrante.ci_jugador,
                equipo["id_torneo"],
                integrante.numero_camiseta
            )

        repo.actualizar_capitan(conn, id_equipo, datos.ci_capitan)

        resultado = {
            "id_equipo": id_equipo,
            "integrantes": repo.listar(conn, id_equipo),
            "ci_capitan": datos.ci_capitan
        }

        conn.commit()
        return resultado

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)

def quitar_integrante(conn, id_equipo: int, ci: str):
    """Saca a un jugador del plantel. Si era el capitán, el equipo queda sin capitán."""
    try:
        equipo = repo.bloquear_equipo(conn, id_equipo)
        if not equipo:
            raise HTTPException(404, "No se encontró el equipo")

        if not repo.torneo_en_inscripcion(conn, equipo["id_torneo"]):
            raise HTTPException(
                409,
                "El plantel solamente puede modificarse durante la inscripción"
            )

        if not repo.es_integrante(conn, id_equipo, ci):
            raise HTTPException(404, "El jugador no integra el plantel de este equipo")

        if equipo["ci_capitan"] == ci:
            repo.quitar_capitan(conn, id_equipo)

        repo.eliminar_integrante(conn, id_equipo, ci)
        conn.commit()

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)


MAX_JUGADORES = 10
MAX_EXTERNOS = 2  # docentes y funcionarios combinados


def disponibles(conn, id_equipo: int):
    if not repo.obtener_equipo(conn, id_equipo):
        raise HTTPException(404, "No se encontró el equipo")
    return repo.disponibles(conn, id_equipo)


def agregar_integrante(conn, id_equipo: int, datos):
    """Suma un jugador al plantel respetando las mismas reglas que el reemplazo completo."""
    try:
        equipo = repo.bloquear_equipo(conn, id_equipo)
        if not equipo:
            raise HTTPException(404, "No se encontró el equipo")

        if not repo.torneo_en_inscripcion(conn, equipo["id_torneo"]):
            raise HTTPException(
                409,
                "El plantel solamente puede modificarse durante la inscripción"
            )

        plantel = repo.listar(conn, id_equipo)
        if len(plantel) >= MAX_JUGADORES:
            raise HTTPException(400, f"El plantel ya tiene el máximo de {MAX_JUGADORES} jugadores")

        jugadores = repo.obtener_jugadores(conn, [datos.ci_jugador])
        if not jugadores:
            raise HTTPException(404, "El jugador no existe")
        jugador = jugadores[0]

        if jugador["id_facultad"] != equipo["id_facultad"]:
            raise HTTPException(400, "El jugador debe pertenecer a la facultad del equipo")

        if jugador["tipo"] in ("docente", "funcionario"):
            externos = sum(1 for j in plantel if j["tipo"] in ("docente", "funcionario"))
            if externos >= MAX_EXTERNOS:
                raise HTTPException(
                    400, "El plantel admite como máximo dos docentes y funcionarios"
                )

        if repo.es_integrante(conn, id_equipo, datos.ci_jugador) or repo.jugadores_en_otro_equipo(
            conn, [datos.ci_jugador], equipo["id_torneo"], id_equipo
        ):
            raise HTTPException(409, "El jugador ya pertenece a un equipo de esta edición")

        if repo.camiseta_ocupada(conn, id_equipo, datos.numero_camiseta):
            raise HTTPException(
                409, f"La camiseta {datos.numero_camiseta} ya la usa otro jugador del equipo"
            )

        repo.insertar_integrante(
            conn, id_equipo, datos.ci_jugador, equipo["id_torneo"], datos.numero_camiseta
        )
        resultado = {
            "id_equipo": id_equipo,
            "integrantes": repo.listar(conn, id_equipo),
            "ci_capitan": equipo["ci_capitan"],
        }
        conn.commit()
        return resultado

    except HTTPException:
        conn.rollback()
        raise
    except pymysql.MySQLError as e:
        conn.rollback()
        _traducir(e)
