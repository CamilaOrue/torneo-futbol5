from fastapi import APIRouter, Depends

from app.database import get_db_admin
from app.repositories import reporte as repo

router = APIRouter(prefix="/reportes", tags=["reportes"])

@router.get("/jugadores-por-facultad")
def jugadores_por_facultad(conn=Depends(get_db_admin)):
    return repo.jugadores_por_facultad_y_tipo(conn)

@router.get("/promedio-por-estados")
def promedio_por_estados(conn=Depends(get_db_admin)):
    return repo.porcentaje_de_partidos_por_estado(conn)

@router.get("/cantidad-sanciones")
def cantidad_sanciones(conn=Depends(get_db_admin)):
    return repo.cantidad_sanciones_por_eq_motivo(conn)

@router.get("/canchas-usadas")
def canchas_usadas(conn=Depends(get_db_admin)):
    return repo.canchas_mas_usadas(conn)

@router.get("/turnos-usados")
def turnos_usados(conn=Depends(get_db_admin)):
    return repo.turnos_mas_usados(conn)

@router.get("/top-jugadores")
def top_jugadores(conn=Depends(get_db_admin)):
    return repo.top_diez_jugadores(conn)

@router.get("/jugadores-no-planilla")
def jugadores_no_planilla(conn=Depends(get_db_admin)):
    return repo.jugadores_no_en_planilla(conn)

@router.get("/fair-play")
def fair_play(conn=Depends(get_db_admin)):
    return repo.tabla_fair_play(conn)

@router.get("/promedio-goles-partido-fecha")
def promedio_goles_partido_fecha(id_torneo: int, conn=Depends(get_db_admin)):
    return repo.promedio_goles_por_partido_fecha(conn, id_torneo)

@router.get("/promedio-goles-partido-edicion")
def promedio_goles_partido_edicion(id_torneo: int, conn=Depends(get_db_admin)):
    return repo.promedio_goles_por_partido_edicion(conn, id_torneo)