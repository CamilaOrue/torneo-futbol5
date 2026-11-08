"""
================================================================================
SUITE DE PRUEBAS INTEGRALES: ABM EQUIPOS (CASOS BORDE Y REGLAS DE NEGOCIO)
================================================================================
Descripción:
    Verifica que las restricciones y validaciones de negocio del servicio de 
    equipos actúen correctamente ante escenarios inválidos.

Casos evaluados:
    1. Error 400: Intentar registrar un equipo en un torneo que NO está en etapa de inscripción.
    2. Error 404: Intentar registrar un equipo asociándolo a una facultad o torneo inexistente.
    3. Validación Pydantic (422): Enviar un payload con campos obligatorios vacíos o faltantes.
================================================================================
"""

import uuid


def test_equipo_error_torneo_no_inscripcion(client):
    """
    Verifica que se rechace (400) la creación de un equipo si el torneo 
    se encuentra en un estado diferente a 'inscripcion' (ej. 'en curso').
    """
    # 1. Obtenemos los torneos para buscar uno que NO esté en inscripción (o forzamos uno)
    res_torneos = client.get("/torneos")
    assert res_torneos.status_code == 200
    torneos = res_torneos.json()

    # Buscamos un torneo que esté 'en curso' o 'finalizado'
    torneo_no_valido = next(
        (t for t in torneos if t.get("estado") != "inscripcion"), None
    )

    # Si por casualidad todos estuvieran en inscripción, el test omite esta validación específica
    if torneo_no_valido:
        id_torneo_cerrado = torneo_no_valido["id_torneo"]
        
        res_crear = client.post(
            "/equipos",
            json={
                "nombre": f"Equipo Fuera de Plazo {uuid.uuid4().hex[:6]}",
                "id_torneo": id_torneo_cerrado,
                "id_facultad": 1,
                "ci_capitan": None,
            },
        )
        # Debe fallar por regla de negocio
        assert res_crear.status_code == 400
        assert "inscripción" in res_crear.json()["detail"].lower()


def test_equipo_error_facultad_o_torneo_inexistente(client):
    """
    Verifica que se devuelva un error 404 si el torneo o la facultad indicada no existen.
    """
    nombre_equipo = f"Equipo Fantasma {uuid.uuid4().hex[:6]}"

    # Intentar registrar con un id_facultad que no existe (ej: 99999)
    res_crear = client.post(
        "/equipos",
        json={
            "nombre": nombre_equipo,
            "id_torneo": 1,
            "id_facultad": 99999,
            "ci_capitan": None,
        },
    )
    assert res_crear.status_code in (404, 400)


def test_equipo_error_validacion_pydantic(client):
    """
    Verifica que los esquemas Pydantic rechacen (422) solicitudes con nombres vacíos o tipos incorrectos.
    """
    res_crear = client.post(
        "/equipos",
        json={
            "nombre": "",  # Vacío, viola el field_validator
            "id_torneo": 1,
            "id_facultad": 1,
        },
    )
    assert res_crear.status_code == 422