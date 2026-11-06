"""
================================================================================
SUITE DE PRUEBAS UNITARIAS: REGLAS DE NEGOCIO DE PLANTELES (CON MOCKS)
================================================================================
Descripción:
    Utiliza Mocks para inyectar datos simulados directamente en los servicios,
    permitiendo evaluar las reglas de negocio del ABM sin depender del estado 
    real de la base de datos de Docker.
================================================================================
"""

from unittest.mock import patch


# Usamos patch para interceptar el repositorio dentro del servicio de plantel
@patch("app.services.plantel.repo.obtener_equipo")
@patch("app.services.plantel.repo.bloquear_equipo")
@patch("app.services.plantel.repo.torneo_en_inscripcion")
@patch("app.services.plantel.repo.obtener_jugadores")
def test_plantel_rechaza_exceso_docentes(
    mock_jugadores, mock_torneo, mock_bloquear, mock_equipo, client
):
    # 1. Creamos nuestra propia data simulando la Base de Datos
    mock_equipo.return_value = {"id_equipo": 1, "id_torneo": 99, "id_facultad": 1, "ci_capitan": None}
    mock_bloquear.return_value = mock_equipo.return_value
    mock_torneo.return_value = True  # Forzamos que el torneo SIEMPRE esté en inscripción
    
    # Inyectamos 3 jugadores tipo "docente" para forzar el fallo de la regla (máximo 2)
    mock_jugadores.return_value = [
        {"ci": "1111111", "id_facultad": 1, "tipo": "docente"},
        {"ci": "2222222", "id_facultad": 1, "tipo": "docente"},
        {"ci": "3333333", "id_facultad": 1, "tipo": "docente"},
    ]

    # 2. Ejecutamos la petición HTTP
    res = client.put(
        "/equipos/1/plantel",
        json={
            "integrantes": [
                {"ci_jugador": "1111111", "numero_camiseta": 10},
                {"ci_jugador": "2222222", "numero_camiseta": 11},
                {"ci_jugador": "3333333", "numero_camiseta": 12},
            ],
            "ci_capitan": "1111111",
        },
    )

    # 3. Verificamos que la regla de negocio haya bloqueado la operación
    assert res.status_code == 400
    assert "máximo dos docentes" in res.json()["detail"].lower()


@patch("app.services.plantel.repo.obtener_equipo")
@patch("app.services.plantel.repo.bloquear_equipo")
@patch("app.services.plantel.repo.torneo_en_inscripcion")
def test_plantel_rechaza_capitan_externo(
    mock_torneo, mock_bloquear, mock_equipo, client
):
    # 1. Preparamos el entorno simulado
    mock_equipo.return_value = {"id_equipo": 1, "id_torneo": 99, "id_facultad": 1, "ci_capitan": None}
    mock_bloquear.return_value = mock_equipo.return_value
    mock_torneo.return_value = True 

    # 2. Intentamos enviar un capitán ("9999999") que no está en la lista de integrantes
    res = client.put(
        "/equipos/1/plantel",
        json={
            "integrantes": [
                {"ci_jugador": "1111111", "numero_camiseta": 10}
            ],
            "ci_capitan": "9999999", # <-- Cédula que no integra el plantel
        },
    )

    # 3. Verificamos que falle por la regla del capitán
    assert res.status_code == 400
    assert "capitán debe ser uno de los integrantes" in res.json()["detail"].lower()


@patch("app.services.plantel.repo.obtener_equipo")
@patch("app.services.plantel.repo.bloquear_equipo")
@patch("app.services.plantel.repo.torneo_en_inscripcion")
@patch("app.services.plantel.repo.obtener_jugadores")
def test_plantel_rechaza_jugador_otra_facultad(
    mock_jugadores, mock_torneo, mock_bloquear, mock_equipo, client
):
    # 1. El equipo pertenece a la facultad 1
    mock_equipo.return_value = {"id_equipo": 1, "id_torneo": 99, "id_facultad": 1, "ci_capitan": None}
    mock_bloquear.return_value = mock_equipo.return_value
    mock_torneo.return_value = True 
    
    # 2. Uno de los jugadores devueltos por la BD simulada pertenece a la facultad 2
    mock_jugadores.return_value = [
        {"ci": "1111111", "id_facultad": 1, "tipo": "estudiante"},
        {"ci": "2222222", "id_facultad": 2, "tipo": "estudiante"}, # <-- Ajeno a la facultad
    ]

    res = client.put(
        "/equipos/1/plantel",
        json={
            "integrantes": [
                {"ci_jugador": "1111111", "numero_camiseta": 10},
                {"ci_jugador": "2222222", "numero_camiseta": 11},
            ],
            "ci_capitan": "1111111",
        },
    )

    # 3. Verificamos el bloqueo
    assert res.status_code == 400
    assert "facultad del equipo" in res.json()["detail"].lower()