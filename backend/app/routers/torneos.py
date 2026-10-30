from fastapi import APIRouter, Depends, HTTPException, Path

from app.database import get_db_admin
from app.repositories import torneo as repo
from app.schemas.torneo import TorneoOut

router = APIRouter(prefix="/torneos", tags=["torneos"])


@router.get("", response_model=list[TorneoOut])
def listar_torneos(conn=Depends(get_db_admin)):
    return repo.listar(conn)


@router.get("/{id_torneo}", response_model=TorneoOut)
def obtener_torneo(id_torneo: int = Path(ge=1), conn=Depends(get_db_admin)):
    torneo = repo.obtener(conn, id_torneo)
    if not torneo:
        raise HTTPException(404, "Edición no encontrada")
    return torneo
