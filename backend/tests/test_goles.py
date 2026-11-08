"""
================================================================================
SUITE DE PRUEBAS INTEGRALES Y MOCKS: ABM GOLES
================================================================================
Descripción:
    Verifica las reglas de negocio del módulo de Goles (validación de partido, 
    verificación de jugador en planilla y restricciones de tiempo).
================================================================================
"""

from unittest.mock import patch
from datetime import date, timedelta, datetime, timezone


@patch("app.services.gol._ahora")
@patch("app.services.gol.repo.obtener_partido")
@patch("app.services.gol.repo.bloquear_partido")
@patch("app.services.gol.repo.jugador_en_planilla")
def test_registrar_gol_jugador_no_en_planilla(
    mock_jugador_planilla, mock_bloquear, mock_obtener_partido, mock_ahora, client
):
    """
    Verifica que se rechace (400) el registro de un gol si el jugador 
    no figura en la planilla de ese partido.
    """
    # Fijamos el tiempo actual simulado dentro del rango válido de las 48 horas posteriores al partido
    tiempo_fijo = datetime(2026, 11, 2, 20, 0, tzinfo=timezone(timedelta(hours=-3)))
    mock_ahora.return_value = tiempo_fijo

    mock_bloquear.return_value = {"id_partido": 1}
    mock_obtener_partido.return_value = {
        "id_partido": 1,
        "id_torneo": 1,
        "dia": date(2026, 11, 1),  # Partido jugado el 1 de nov (finaliza a las 18:00)
        "estado": "jugado",
        "hora_fin": timedelta(hours=18)
    }
    
    # Simulamos que el jugador NO está en la planilla
    mock_jugador_planilla.return_value = None

    res = client.post(
        "/goles/partido/1",
        json={
            "ci_jugador": "12345678",
            "minuto": 25,
            "autogol": False
        }
    )

    assert res.status_code == 400
    assert "no figura en la planilla" in res.json()["detail"].lower()