from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.database import get_db_admin
from app.repositories import jugador as repo
from app.schemas.jugador import JugadorDetalleOut, JugadorOut, TipoJugador

router = APIRouter(prefix="/jugadores", tags=["jugadores"])


@router.get("", response_model=list[JugadorOut])
def listar_jugadores(
    q: Annotated[str | None, Query(max_length=100, description="Nombre, apellido, CI o email")] = None,
    id_facultad: Annotated[int | None, Query(ge=1)] = None,
    tipo: TipoJugador | None = None,
    conn=Depends(get_db_admin),
):
    return repo.listar(conn, q.strip() if q else None, id_facultad, tipo)


@router.get("/{ci}", response_model=JugadorDetalleOut)
def obtener_jugador(ci: str = Path(pattern=r"^[0-9]{7,8}$"), conn=Depends(get_db_admin)):
    jugador = repo.obtener(conn, ci)
    if not jugador:
        raise HTTPException(404, "Jugador no encontrado")
    return {**jugador, "equipos": repo.equipos_de(conn, ci)}
