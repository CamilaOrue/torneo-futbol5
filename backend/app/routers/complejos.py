import pymysql

from fastapi import APIRouter, Depends, HTTPException, Path

from app.database import get_db_admin
from app.repositories import complejo as repo
from app.schemas.complejo import ComplejoCreate, ComplejoOut


router = APIRouter(prefix="/complejos", tags=["complejos"])

@router.get("", response_model=list[ComplejoOut])
def listar_complejos(conn=Depends(get_db_admin)):
    return repo.listar(conn)


@router.get("/{id_complejo}", response_model=ComplejoOut)
def obtener_complejo(
    id_complejo: int = Path(ge=1),
    conn=Depends(get_db_admin)
):
    complejo = repo.obtener(conn, id_complejo)

    if not complejo:
        raise HTTPException(404, "Complejo no encontrado")

    return complejo


@router.post("", response_model=ComplejoOut, status_code=201)
def crear_complejo(
    datos: ComplejoCreate,
    conn=Depends(get_db_admin)
):
    try:
        return repo.crear(conn, datos.model_dump())
    except pymysql.err.IntegrityError:
        raise HTTPException(
            409,
            "Ya existe un complejo con ese nombre"
        )


@router.put("/{id_complejo}", response_model=ComplejoOut)
def modificar_complejo(
    datos: ComplejoCreate,
    id_complejo: int = Path(ge=1),
    conn=Depends(get_db_admin)
):
    if not repo.obtener(conn, id_complejo):
        raise HTTPException(404, "Complejo no encontrado")

    try:
        return repo.modificar(conn, id_complejo, datos.model_dump())
    except pymysql.err.IntegrityError:
        raise HTTPException(
            409,
            "Ya existe otro complejo con ese nombre"
        )


@router.delete("/{id_complejo}", status_code=204)
def eliminar_complejo(
    id_complejo: int = Path(ge=1),
    conn=Depends(get_db_admin)
):
    if not repo.obtener(conn, id_complejo):
        raise HTTPException(404, "Complejo no encontrado")

    try:
        repo.eliminar(conn, id_complejo)
    except pymysql.err.IntegrityError:
        raise HTTPException(
            409,
            "No se puede eliminar el complejo porque tiene canchas asociadas"
        )
