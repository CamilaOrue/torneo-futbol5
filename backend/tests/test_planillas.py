"""
================================================================================
SUITE DE PRUEBAS INTEGRALES Y MOCKS: ABM PLANILLAS
================================================================================
Descripción:
    Verifica las validaciones de negocio del módulo de Planillas (tiempos de partido, 
    cantidad mínima de jugadores por equipo y unicidad de cédulas) mediante Mocks.
================================================================================
"""

from unittest.mock import patch
from datetime import date, timedelta


@patch("app.services.planilla.repo.obtener_partido")
@patch("app.services.planilla.repo.bloquear_partido")
@patch("app.services.planilla._validar_partido_para_planilla")
@patch("app.services.planilla.repo.obtener_jugadores_equipo")
@patch("app.services.planilla.sancion_repo.esta_suspendido")
@patch("app.services.planilla.repo.listar")
def test_registrar_planilla_equipo_insuficiente(
    mock_listar, mock_suspendido, mock_obtener_jugadores, mock_validar_tiempo, mock_bloquear, mock_obtener_partido, client
):
    """
    Verifica que se rechace (400) el registro si alguno de los equipos 
    tiene menos de 5 jugadores en la planilla.
    """
    mock_bloquear.return_value = {"id_partido": 1}
    mock_obtener_partido.return_value = {
        "id_partido": 1,
        "id_torneo": 1,
        "numero_fecha": 1,
        "id_equipo_local": 10,
        "id_equipo_visitante": 20,
        "dia": date(2026, 11, 1),
        "id_turno": 1,
        "estado": "programado",
        "hora_fin": timedelta(hours=20)
    }
    mock_validar_tiempo.return_value = None  # Salta validación de horario
    
    # Definimos exactamente las cédulas que vamos a enviar
    cedulas_locales = [
        "11111111", "22222222", "33333333", "44444444" # Solo 4 jugadores (menor al mínimo de 5)
    ]
    cedulas_visitantes = [
        "55555555", "66666666", "77777777", "88888888", "99999999", "10101010" # 6 visitantes
    ]
    todas_cedulas = cedulas_locales + cedulas_visitantes

    # Configuramos el mock para que devuelva los jugadores correspondientes a cada equipo
    # de modo que pasen la primera validación pero fallen por cantidad mínima en locales.
    mock_obtener_jugadores.side_effect = [
        # Jugadores locales encontrados (solo 4)
        [
            {"ci_jugador": ci, "id_equipo": 10, "nombre": "Jugador", "apellido": "Local"}
            for ci in cedulas_locales
        ],
        # Jugadores visitantes encontrados (6)
        [
            {"ci_jugador": ci, "id_equipo": 20, "nombre": "Jugador", "apellido": "Visitante"}
            for ci in cedulas_visitantes
        ]
    ]
    
    mock_suspendido.return_value = False
    mock_listar.return_value = []

    res = client.put(
        "/planillas/1",
        json={"ci_jugadores": todas_cedulas}
    )

    assert res.status_code == 400
    assert "equipo local debe tener al menos 5 jugadores" in res.json()["detail"].lower()