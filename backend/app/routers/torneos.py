from fastapi import APIRouter, Depends, HTTPException, Path

from app.database import get_db_admin
from app.repositories import torneo as repo
from app.schemas.torneo import TorneoCreate, TorneoEstadoUpdate, TorneoOut
from app.security import requiere_rol
from app.services import torneo as service

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


@router.post(
    "",
    response_model=TorneoOut,
    status_code=201,
    dependencies=[Depends(requiere_rol("administrador"))],
)
def crear_torneo(datos: TorneoCreate, conn=Depends(get_db_admin)):
    return service.crear_torneo(conn, datos)


@router.patch(
    "/{id_torneo}/estado",
    response_model=TorneoOut,
    dependencies=[Depends(requiere_rol("administrador"))],
)
def cambiar_estado_torneo(
    datos: TorneoEstadoUpdate,
    id_torneo: int = Path(ge=1),
    conn=Depends(get_db_admin),
):
    return service.cambiar_estado(conn, id_torneo, datos.estado)