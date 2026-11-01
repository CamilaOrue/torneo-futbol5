
import pymysql

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.database import get_db_admin
from app.repositories import cancha as repo
from app.repositories import complejo as complejo_repo
from app.schemas.cancha import CanchaCreate, CanchaOut, CanchaUpdate


router = APIRouter(prefix="/canchas", tags=["canchas"])


@router.get("", response_model=list[CanchaOut])
def listar_canchas(
    id_complejo: int | None = Query(default=None, ge=1),
    conn=Depends(get_db_admin)
):
    return repo.listar(conn, id_complejo)


@router.get("/{id_complejo}/{nombre_cancha}", response_model=CanchaOut)
def obtener_cancha(
    id_complejo: int = Path(ge=1),
    nombre_cancha: str = Path(min_length=1, max_length=50),
    conn=Depends(get_db_admin)
):
    cancha = repo.obtener(conn, id_complejo, nombre_cancha)

    if not cancha:
        raise HTTPException(404, "Cancha no encontrada")

    return cancha


@router.post("", response_model=CanchaOut, status_code=201)
def crear_cancha(
    datos: CanchaCreate,
    conn=Depends(get_db_admin)
):
    if not complejo_repo.obtener(conn, datos.id_complejo):
        raise HTTPException(404, "El complejo indicado no existe")

    try:
        return repo.crear(conn, datos.model_dump())
    except pymysql.err.IntegrityError:
        raise HTTPException(
            409,
            "Ya existe una cancha con ese nombre en el complejo"
        )


@router.put(
    "/{id_complejo}/{nombre_cancha}",
    response_model=CanchaOut
)
def modificar_cancha(
    datos: CanchaUpdate,
    id_complejo: int = Path(ge=1),
    nombre_cancha: str = Path(min_length=1, max_length=50),
    conn=Depends(get_db_admin)
):
    if not repo.obtener(conn, id_complejo, nombre_cancha):
        raise HTTPException(404, "Cancha no encontrada")

    return repo.modificar(
        conn,
        id_complejo,
        nombre_cancha,
        datos.model_dump()
    )


@router.delete("/{id_complejo}/{nombre_cancha}", status_code=204)
def eliminar_cancha(
    id_complejo: int = Path(ge=1),
    nombre_cancha: str = Path(min_length=1, max_length=50),
    conn=Depends(get_db_admin)
):
    if not repo.obtener(conn, id_complejo, nombre_cancha):
        raise HTTPException(404, "Cancha no encontrada")

    try:
        repo.eliminar(conn, id_complejo, nombre_cancha)
    except pymysql.err.IntegrityError:
        raise HTTPException(
            409,
            "No se puede eliminar la cancha porque está asociada a un partido"
        )
