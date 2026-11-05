from fastapi import APIRouter, Depends, HTTPException, Path, Response
import pymysql

from app.database import get_db_admin
from app.errors import error_campo
from app.repositories import plantel as repo
from app.schemas.plantel import (
    PlantelCreate,
    PlantelUpdate,
    JugadorPlantelOut,
)

router = APIRouter(tags=["planteles"])

personalUni = ("docente", "funcionario")


def _validar_equipo_en_inscripcion(conn, equipo):
    if not repo.torneo_en_inscripcion(conn, equipo["id_torneo"]):
        raise HTTPException(
            409, "El plantel solo puede modificarse durante la inscripción"
        )


#--------------------------------------------------------- Lectura
@router.get(
    "/equipos/{id_equipo}/plantel",
    response_model=list[JugadorPlantelOut],
)
def listar_plantel(
    id_equipo: int = Path(ge=1),
    conn=Depends(get_db_admin),
):
    equipo = repo.obtener_equipo(conn, id_equipo)

    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")

    return repo.listar(conn, id_equipo)


#--------------------------------------------------------- Modificaciones
@router.post(
    "/equipos/{id_equipo}/plantel",
    response_model=list[JugadorPlantelOut],
    status_code=201,
)
def agregar_jugador(
    datos: PlantelCreate,
    id_equipo: int = Path(ge=1),
    conn=Depends(get_db_admin),
):
    equipo = repo.obtener_equipo(conn, id_equipo)

    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")

    # Solo se modifica el plantel durante la inscripción
    _validar_equipo_en_inscripcion(conn, equipo)

    jugador = repo.obtener_jugador(conn, datos.ci_jugador)

    if not jugador:
        raise error_campo(
            404, "ci_jugador", "Jugador no encontrado"
        )

    #El jugador debe pertenecer a la facultad del equipo
    if jugador["id_facultad"] != equipo["id_facultad"]:
        raise error_campo(
            409, "ci_jugador",
            "El jugador debe pertenecer a la misma facultad que el equipo",
        )

    #El equipo no puede superar los 10 integrantes
    if repo.cantidad(conn, id_equipo) >= 10:
        raise error_campo(
            409, "ci_jugador",
            "El plantel ya alcanzó el máximo de 10 jugadores",
        )

    #Máximo combinado de 2 docentes y funcionarios
    if jugador["tipo"] in personalUni:
        if repo.cantidad_externos(conn, id_equipo) >= 2:
            raise error_campo(
                409, "ci_jugador",
                "El equipo ya tiene el máximo de 2 docentes/funcionarios",
            )

    #Insertar al jugador
    try:
        repo.agregar(
            conn,
            id_equipo,
            datos.ci_jugador,
            equipo["id_torneo"],
            datos.numero_camiseta,
        )
        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        http = _traducir(e)
        if http:
            raise http from e
        raise

    return repo.listar(conn, id_equipo)


@router.put(
    "/equipos/{id_equipo}/plantel/{ci}",
    response_model=list[JugadorPlantelOut],
)
def actualizar_camiseta(
    datos: PlantelUpdate,
    id_equipo: int = Path(ge=1),
    ci: str = Path(pattern=r"^[0-9]{7,8}$"),
    conn=Depends(get_db_admin),
):
    equipo = repo.obtener_equipo(conn, id_equipo)

    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")

    _validar_equipo_en_inscripcion(conn, equipo)

    if not any(j["ci"] == ci for j in repo.listar(conn, id_equipo)):
        raise HTTPException(
            404, "El jugador no pertenece al plantel de este equipo"
        )

    try:
        repo.actualizar_camiseta(
            conn, id_equipo, ci, datos.numero_camiseta
        )
        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        http = _traducir(e)
        if http:
            raise http from e
        raise

    return repo.listar(conn, id_equipo)


@router.delete(
    "/equipos/{id_equipo}/plantel/{ci}",
    status_code=204,
)
def eliminar_jugador(
    id_equipo: int = Path(ge=1),
    ci: str = Path(pattern=r"^[0-9]{7,8}$"),
    conn=Depends(get_db_admin),
):
    equipo = repo.obtener_equipo(conn, id_equipo)

    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")

    _validar_equipo_en_inscripcion(conn, equipo)

    if not any(j["ci"] == ci for j in repo.listar(conn, id_equipo)):
        raise HTTPException(
            404, "El jugador no pertenece al plantel de este equipo"
        )

    # No se puede quitar al capitán sin asignar otro primero
    if equipo["ci_capitan"] == ci:
        raise error_campo(
            409, "ci",
            "No se puede quitar al capitán. Primero asigná otro capitán",
        )

    try:
        repo.eliminar(conn, id_equipo, ci)
        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        http = _traducir(e)
        if http:
            raise http from e
        raise

    return Response(status_code=204)