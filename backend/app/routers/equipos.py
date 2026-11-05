from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
import pymysql

from app.database import get_db_admin
from app.errors import error_campo
from app.repositories import equipo as repo
from app.schemas.equipo import (
    EquipoCreate,
    EquipoDetalleOut,
    EquipoOut,
    EquipoUpdate,
    CapitanUpdate,
)

router = APIRouter(prefix="/equipos", tags=["equipos"])

def _traducir(e: pymysql.MySQLError) -> HTTPException | None:
    codigo = e.args[0]
    mensaje = str(e.args[1]) if len(e.args) > 1 else ""

    if codigo == 1062:
        if "uq_equipo_nombre" in mensaje or "nombre" in mensaje:
            return error_campo(
                409, "nombre",
                "Ya existe un equipo con ese nombre en esta edición",
            )
        return HTTPException(409, "Ya existe un registro con esos datos")

    if codigo == 1452:
        return HTTPException(
            422, "El torneo, la facultad o el capitán indicado no existe"
        )

    if codigo in (1451, 1217):
        return HTTPException(
            409,
            "No se puede eliminar el equipo porque tiene plantel, partidos "
            "u otros registros asociados",
        )

    return None


#--------------------------------------------------------------- lectura
@router.get("", response_model=list[EquipoOut])
def listar_equipos(
    id_torneo: int | None = Query(default=None, ge=1, description="Filtra por edición"),
    conn=Depends(get_db_admin),
):
    return repo.listar(conn, id_torneo)


@router.get("/{id_equipo}", response_model=EquipoDetalleOut)
def obtener_equipo(id_equipo: int = Path(ge=1), conn=Depends(get_db_admin)):
    equipo = repo.obtener(conn, id_equipo)
    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")
    return {**equipo, "plantel": repo.plantel(conn, id_equipo)}


#--------------------------------------------------------------- alta
@router.post("", response_model=EquipoOut, status_code=201)
def crear_equipo(datos: EquipoCreate, conn=Depends(get_db_admin)):

    if not repo.existe_facultad(conn, datos.id_facultad):
        raise error_campo(
            422, "id_facultad", "La facultad indicada no existe"
        )

    if not repo.torneo_en_inscripcion(conn, datos.id_torneo):
        raise error_campo(
            409, "id_torneo",
            "Solo se pueden crear equipos en torneos en inscripción",
        )

    try:
        id_equipo = repo.crear(conn, datos.model_dump())
        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        http = _traducir(e)
        if http:
            raise http from e
        raise

    return repo.obtener(conn, id_equipo)


#--------------------------------------------------------------- modificaciones
@router.put("/{id_equipo}", response_model=EquipoDetalleOut)
def actualizar_equipo(
    id_equipo: int = Path(ge=1),
    equipo: EquipoUpdate = None,
    conn=Depends(get_db_admin)
):
    update_equipo = repo.bloquear(conn, id_equipo)

    if not update_equipo:
        raise HTTPException(404, "Equipo no encontrado")

    if not repo.torneo_en_inscripcion(conn, update_equipo["id_torneo"]):
        raise HTTPException(
            409, "Solo se pueden modificar equipos durante la inscripción"
        )

    if not repo.existe_facultad(conn, equipo.id_facultad):
        raise error_campo(
            422, "id_facultad", "La facultad indicada no existe"
        )

    # Si ya hay jugadores, todos deben pertenecer a la nueva facultad.
    # Por est, no permitimos cambiarla mientras el equipo tenga integrantes.
    if equipo.id_facultad != update_equipo["id_facultad"]:
        if repo.plantel(conn, id_equipo):
            raise error_campo(
                409, "id_facultad",
                "No se puede cambiar la facultad de un equipo que ya tiene plantel",
            )

    try:
        repo.actualizar(conn, id_equipo, equipo.model_dump())
        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        http = _traducir(e)
        if http:
            raise http from e
        raise

    return repo.obtener(conn, id_equipo)


@router.patch("/{id_equipo}/capitan", response_model=EquipoOut)
def asignar_capitan(
    capitan: CapitanUpdate,
    id_equipo: int = Path(ge=1),
    conn=Depends(get_db_admin),
):
    update_capitan = repo.bloquear(conn, id_equipo)

    if not update_capitan:
        raise HTTPException(404, "Equipo no encontrado")

    if not repo.torneo_en_inscripcion(conn, update_capitan["id_torneo"]):
        raise HTTPException(
            409, "Solo se puede modificar el capitán durante la inscripción"
        )

    if not repo.existe_capitan_en_plantel(
        conn, id_equipo, capitan.ci_capitan
    ):
        raise error_campo(
            409, "ci_capitan",
            "El capitán debe pertenecer al plantel del equipo",
        )

    try:
        repo.asignar_capitan(conn, id_equipo, capitan.ci_capitan)
        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        http = _traducir(e)
        if http:
            raise http from e
        raise

    return repo.obtener(conn, id_equipo)


#--------------------------------------------------------------- baja
@router.delete("/{id_equipo}", status_code=204)
def eliminar_equipo(
    id_equipo: int = Path(ge=1),
    conn=Depends(get_db_admin),
):
    actual = repo.bloquear(conn, id_equipo)

    if not actual:
        raise HTTPException(404, "Equipo no encontrado")

    if not repo.torneo_en_inscripcion(conn, actual["id_torneo"]):
        raise HTTPException(
            409, "Solo se pueden eliminar equipos durante la inscripción"
        )

    try:
        repo.eliminar(conn, id_equipo)
        conn.commit()

    except pymysql.MySQLError as e:
        conn.rollback()
        http = _traducir(e)
        if http:
            raise http from e
        raise

    return Response(status_code=204)