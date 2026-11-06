from fastapi import HTTPException

from app.repositories import torneo as repo


# Cambios de estado permitidos para una edición del torneo
CAMBIOS_PERMITIDOS = {
    "inscripcion": ["en curso"],
    "en curso": ["finalizado"],
    "finalizado": [],
}


# ---------------------------------------------------------------- verificaciones

def verificar_existe(torneo):
    if torneo is None:
        raise HTTPException(404, "La edición no existe")


def verificar_edicion_unica(conn, anio, semestre):
    if repo.existe_edicion(conn, anio, semestre):
        raise HTTPException(409, f"Ya existe una edición para el semestre {semestre} de {anio}")


def verificar_cambio_valido(estado_actual, nuevo_estado):
    if nuevo_estado not in CAMBIOS_PERMITIDOS[estado_actual]:
        raise HTTPException(409, f"No se puede pasar de '{estado_actual}' a '{nuevo_estado}'")


# ---------------------------------------------------------------- operaciones

def crear_torneo(conn, datos):
    try:
        verificar_edicion_unica(conn, datos.anio, datos.semestre)
        id_torneo = repo.insertar_torneo(conn, datos)
        conn.commit()
        return repo.obtener(conn, id_torneo)

    except Exception:
        conn.rollback()
        raise


def cambiar_estado(conn, id_torneo, nuevo_estado):
    try:
        torneo = repo.obtener(conn, id_torneo)
        verificar_existe(torneo)
        verificar_cambio_valido(torneo["estado"], nuevo_estado)
        repo.actualizar_estado(conn, id_torneo, nuevo_estado)
        conn.commit()
        return repo.obtener(conn, id_torneo)

    except Exception:
        conn.rollback()
        raise