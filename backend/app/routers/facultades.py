from fastapi import APIRouter, Depends

from app.repositories import facultad as repo
from app.schemas.facultad import FacultadOut
from app.security import get_db_segun_rol, requiere_rol

router = APIRouter(
    prefix="/facultades",
    tags=["facultades"],
    dependencies=[Depends(requiere_rol("administrador", "planillero"))],
)


@router.get("", response_model=list[FacultadOut])
def listar_facultades(conn=Depends(get_db_segun_rol)):
    return repo.listar(conn)
