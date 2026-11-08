"""
================================================================================
SUITE DE PRUEBAS INTEGRALES Y MOCKS: ABM SANCIONES
================================================================================
Descripción:
    Verifica las validaciones de negocio del módulo de Sanciones mediante Mocking.
================================================================================
"""

from unittest.mock import patch


@patch("app.services.sancion.repo.jugador_inscripto_en_torneo")
def test_crear_sancion_motivo_no_disciplinario(mock_inscripto, client):
    """
    Verifica que se rechace (400) la creación manual de una sanción si el motivo
    es 'roja' o 'acumulacion_amarillas', ya que deben generarse automáticamente.
    """
    res = client.post(
        "/sanciones/",
        json={
            "ci_jugador": "12345678",
            "id_torneo": 1,
            "motivo": "roja",
            "numero_fecha_inicio": 1,
            "cantidad_fechas": 2
        }
    )
    assert res.status_code == 400
    assert "automáticamente" in res.json()["detail"].lower()


@patch("app.services.sancion.repo.jugador_inscripto_en_torneo")
def test_crear_sancion_jugador_no_inscripto(mock_inscripto, client):
    """
    Verifica que se rechace (400) si el jugador no forma parte de ningún equipo del torneo.
    """
    mock_inscripto.return_value = None  # Simula que el jugador no está inscripto

    res = client.post(
        "/sanciones/",
        json={
            "ci_jugador": "87654321",
            "id_torneo": 1,
            "motivo": "disciplinaria",
            "numero_fecha_inicio": 1,
            "cantidad_fechas": 1
        }
    )
    assert res.status_code == 400
    assert "no está inscripto" in res.json()["detail"].lower()