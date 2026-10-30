from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
import pymysql

from app.database import get_db_admin
from app.errors import error_campo
from app.repositories import jugador as repo
from app.schemas.jugador import (
    JugadorCreate,
    JugadorDetalleOut,
    JugadorOut,
    JugadorUpdate,
    TipoJugador,
)

router = APIRouter(prefix="/jugadores", tags=["jugadores"])

CI_PATH = Path(pattern=r"^[0-9]{7,8}$", description="CI sin puntos ni guión")
EXTERNOS = ("docente", "funcionario")  # máximo 2 por plantel


def _traducir(e: pymysql.MySQLError) -> HTTPException | None:
    """Convierte errores de MySQL en respuestas HTTP claras; None si no se reconoce."""
    codigo = e.args[0]
    mensaje = str(e.args[1]) if len(e.args) > 1 else ""
    if codigo == 1062:
        if "PRIMARY" in mensaje:
            return error_campo(409, "ci", "Ya existe un jugador con esa CI")
        if "email" in mensaje:
            return error_campo(409, "email", "Ya existe un jugador con ese email")
        return HTTPException(409, "Ya existe un registro con esos datos")
    if codigo == 1452:
        return error_campo(422, "id_facultad", "La facultad indicada no existe")
    if codigo == 3819:
        return HTTPException(422, "Los datos no cumplen las restricciones de la base de datos")
    if codigo in (1451, 1217):  # fila referenciada por otra tabla
        return HTTPException(
            409,
            "No se puede eliminar al jugador: integra un plantel, es capitán de un equipo "
            "o tiene sanciones registradas",
        )
    return None


# ---------------------------------------------------------------- lectura
@router.get("", response_model=list[JugadorOut])
def listar_jugadores(
    q: Annotated[str | None, Query(max_length=100, description="Nombre, apellido, CI o email")] = None,
    id_facultad: Annotated[int | None, Query(ge=1)] = None,
    tipo: TipoJugador | None = None,
    conn=Depends(get_db_admin),
):
    return repo.listar(conn, q.strip() if q else None, id_facultad, tipo)


@router.get("/{ci}", response_model=JugadorDetalleOut)
def obtener_jugador(ci: str = CI_PATH, conn=Depends(get_db_admin)):
    jugador = repo.obtener(conn, ci)
    if not jugador:
        raise HTTPException(404, "Jugador no encontrado")
    return {**jugador, "equipos": repo.equipos_de(conn, ci)}


# ---------------------------------------------------------------- alta
@router.post("", response_model=JugadorOut, status_code=201)
def crear_jugador(datos: JugadorCreate, conn=Depends(get_db_admin)):
    if not repo.existe_facultad(conn, datos.id_facultad):
        raise error_campo(422, "id_facultad", "La facultad indicada no existe")
    try:
        repo.crear(conn, datos.model_dump())
        conn.commit()
    except pymysql.MySQLError as e:
        conn.rollback()
        http = _traducir(e)
        if http:
            raise http from e
        raise
    return repo.obtener(conn, datos.ci)


# ---------------------------------------------------------------- modificación
@router.put("/{ci}", response_model=JugadorOut)
def actualizar_jugador(datos: JugadorUpdate, ci: str = CI_PATH, conn=Depends(get_db_admin)):
    actual = repo.bloquear(conn, ci)
    if not actual:
        raise HTTPException(404, "Jugador no encontrado")
    if not repo.existe_facultad(conn, datos.id_facultad):
        raise error_campo(422, "id_facultad", "La facultad indicada no existe")

    # Todos los jugadores de un plantel deben pertenecer a la facultad del equipo.
    conflictos = repo.planteles_de_otra_facultad(conn, ci, datos.id_facultad)
    if conflictos:
        raise error_campo(
            409, "id_facultad",
            f"No se puede cambiar la facultad: integra el plantel de {', '.join(conflictos)}, "
            "que representa a otra facultad",
        )

    # Cada plantel admite como máximo 2 docentes/funcionarios.
    if datos.tipo in EXTERNOS and actual["tipo"] not in EXTERNOS:
        sin_cupo = repo.planteles_sin_cupo_externo(conn, ci)
        if sin_cupo:
            raise error_campo(
                409, "tipo",
                f"No se puede cambiar el tipo: el plantel de {', '.join(sin_cupo)} "
                "ya tiene 2 docentes/funcionarios",
            )

    try:
        repo.actualizar(conn, ci, datos.model_dump())
        conn.commit()
    except pymysql.MySQLError as e:
        conn.rollback()
        http = _traducir(e)
        if http:
            raise http from e
        raise
    return repo.obtener(conn, ci)


# ---------------------------------------------------------------- baja
@router.delete("/{ci}", status_code=204)
def eliminar_jugador(ci: str = CI_PATH, conn=Depends(get_db_admin)):
    if not repo.bloquear(conn, ci):
        raise HTTPException(404, "Jugador no encontrado")
    try:
        repo.eliminar(conn, ci)
        conn.commit()
    except pymysql.MySQLError as e:
        conn.rollback()
        http = _traducir(e)
        if http:
            raise http from e
        raise
    return Response(status_code=204)
