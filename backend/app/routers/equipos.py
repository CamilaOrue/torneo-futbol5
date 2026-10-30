from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.database import get_db_admin
from app.repositories import equipo as repo
from app.schemas.equipo import EquipoDetalleOut, EquipoOut

router = APIRouter(prefix="/equipos", tags=["equipos"])


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
