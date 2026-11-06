"""
================================================================================
SUITE DE PRUEBAS INTEGRALES Y MOCKS: ABM PARTIDOS
================================================================================
Descripción:
    Prueba el router HTTP inyectando repositorios mockeados, permitiendo
    saltar la validación rigurosa de las reglas de negocio en base de datos.
================================================================================
"""

from unittest.mock import patch
from datetime import date, timedelta


@patch("app.services.partido.repo.crear")
@patch("app.services.partido.repo.obtener")
@patch("app.services.partido._validar_programacion")
def test_crear_partido_mock(mock_validar, mock_obtener, mock_crear, client):
    # Simulamos el ID insertado
    mock_crear.return_value = 100
    
    # Simulamos la respuesta final de la BDD
    mock_obtener.return_value = {
        "id_partido": 100,
        "id_torneo": 1,
        "numero_fecha": 1,
        "id_equipo_local": 2,
        "id_equipo_visitante": 3,
        "dia": date(2026, 12, 1),
        "id_turno": 1,
        "nombre_cancha": "Cancha Central",
        "id_complejo": 1,
        "estado": "programado",
        "hora_inicio": timedelta(hours=18),
        "hora_fin": timedelta(hours=19),
    }
    
    # Saltamos (mock) todas las validaciones complejas de BDD devolviendo un "Pase libre"
    mock_validar.return_value = None

    res = client.post(
        "/partidos/",
        json={
            "id_torneo": 1,
            "numero_fecha": 1,
            "id_equipo_local": 2,
            "id_equipo_visitante": 3,
            "dia": "2026-12-01",
            "id_turno": 1,
            "nombre_cancha": "Cancha Central",
            "id_complejo": 1
        },
    )

    assert res.status_code == 201
    data = res.json()
    assert data["id_partido"] == 100
    assert data["estado"] == "programado"


@patch("app.services.partido.repo.bloquear_partido")
@patch("app.services.partido.repo.actualizar_estado")
@patch("app.services.partido.repo.obtener")
def test_cambiar_estado_partido_mock(mock_obtener, mock_actualizar, mock_bloquear, client):
    # Simulamos que existe el partido en estado programado
    mock_bloquear.return_value = {
        "id_partido": 100,
        "estado": "programado",
    }

    # Simulamos el objeto devuelto luego de modificar el estado
    mock_obtener.return_value = {
        "id_partido": 100,
        "id_torneo": 1,
        "numero_fecha": 1,
        "id_equipo_local": 2,
        "id_equipo_visitante": 3,
        "dia": date(2026, 12, 1),
        "id_turno": 1,
        "nombre_cancha": "Cancha Central",
        "id_complejo": 1,
        "estado": "postergado",
        "hora_inicio": timedelta(hours=18),
        "hora_fin": timedelta(hours=19),
    }

    res = client.patch(
        "/partidos/100/estado",
        json={"estado": "postergado"}
    )

    assert res.status_code == 200
    assert res.json()["estado"] == "postergado"