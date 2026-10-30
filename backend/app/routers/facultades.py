from fastapi import APIRouter, Depends

from app.database import get_db_admin
from app.repositories import facultad as repo
from app.schemas.facultad import FacultadOut

router = APIRouter(prefix="/facultades", tags=["facultades"])


@router.get("", response_model=list[FacultadOut])
def listar_facultades(conn=Depends(get_db_admin)):
    return repo.listar(conn)
