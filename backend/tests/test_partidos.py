"""
================================================================================
SUITE DE PRUEBAS INTEGRALES Y MOCKS: ABM PARTIDOS
================================================================================
Descripción:
    Prueba el router HTTP inyectando repositorios mockeados, permitiendo
    saltar la validación rigurosa de las reglas de negocio en base de datos.
================================================================================
"""

from unittest.mock import MagicMock, patch
from datetime import date, timedelta

import pytest

from app.database import get_db_admin
from app.main import app
from app.routers import partidos as partidos_router
from app.security import crear_token, get_db_segun_rol, get_usuario_actual


@pytest.fixture
def sin_base_de_datos():
    # Los tests no usan MySQL: cada request recibe una conexión falsa
    def conexion_falsa():
        yield MagicMock()

    app.dependency_overrides[get_db_admin] = conexion_falsa
    app.dependency_overrides[get_db_segun_rol] = conexion_falsa
    yield
    app.dependency_overrides.pop(get_db_admin, None)
    app.dependency_overrides.pop(get_db_segun_rol, None)


@pytest.fixture
def como_administrador():
    # Los endpoints de escritura de partidos exigen rol administrador
    app.dependency_overrides[get_usuario_actual] = lambda: {"correo": "admin@ucu.edu.uy", "rol": "administrador"}
    yield
    app.dependency_overrides.pop(get_usuario_actual, None)


@pytest.mark.usefixtures("sin_base_de_datos", "como_administrador")
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


@pytest.mark.usefixtures("sin_base_de_datos", "como_administrador")
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


# ------------------------------------------------------------------------------
# PERMISOS: consultar (administrador y planillero) / escribir (solo administrador)
# ------------------------------------------------------------------------------

DATOS = {
    "id_torneo": 1,
    "numero_fecha": 1,
    "id_equipo_local": 2,
    "id_equipo_visitante": 3,
    "dia": "2026-12-01",
    "id_turno": 1,
    "nombre_cancha": "Cancha Central",
    "id_complejo": 1,
}

PARTIDO = {
    **DATOS,
    "id_partido": 100,
    "estado": "programado",
    "hora_inicio": "18:00:00",
    "hora_fin": "19:00:00",
}

# (método, ruta, cuerpo, función del servicio que escribe, status si tiene permiso)
ESCRITURAS = [
    pytest.param("POST", "/partidos/", DATOS, "crear", 201, id="alta"),
    pytest.param("PUT", "/partidos/100", DATOS, "actualizar", 200, id="modificacion"),
    pytest.param("PATCH", "/partidos/100/estado", {"estado": "postergado"}, "cambiar_estado", 200, id="estado"),
    pytest.param("DELETE", "/partidos/100", None, "eliminar", 204, id="baja"),
]

LECTURAS = [
    pytest.param("/partidos/", "listar", [PARTIDO], id="listar"),
    pytest.param("/partidos/100", "obtener", PARTIDO, id="obtener"),
]


def headers_de(rol: str) -> dict:
    """Header Authorization de un usuario con el rol indicado."""
    return {"Authorization": f"Bearer {crear_token(f'{rol}@ucu.edu.uy', rol)}"}


@pytest.fixture
def service(monkeypatch, sin_base_de_datos):
    falso = MagicMock()
    for metodo in ("crear", "actualizar", "cambiar_estado", "obtener"):
        getattr(falso, metodo).return_value = PARTIDO
    falso.listar.return_value = [PARTIDO]
    monkeypatch.setattr(partidos_router, "service", falso)
    return falso


@pytest.mark.parametrize("metodo, ruta, cuerpo, escritura, esperado", ESCRITURAS)
def test_administrador_puede_escribir(client, service, metodo, ruta, cuerpo, escritura, esperado):
    res = client.request(metodo, ruta, json=cuerpo, headers=headers_de("administrador"))

    assert res.status_code == esperado
    getattr(service, escritura).assert_called_once()


@pytest.mark.parametrize("metodo, ruta, cuerpo, escritura, esperado", ESCRITURAS)
def test_planillero_recibe_403_y_no_escribe(client, service, metodo, ruta, cuerpo, escritura, esperado):
    res = client.request(metodo, ruta, json=cuerpo, headers=headers_de("planillero"))

    assert res.status_code == 403
    getattr(service, escritura).assert_not_called()


@pytest.mark.parametrize("metodo, ruta, cuerpo, escritura, esperado", ESCRITURAS)
def test_sin_token_recibe_401_y_no_escribe(client, service, metodo, ruta, cuerpo, escritura, esperado):
    res = client.request(metodo, ruta, json=cuerpo)

    assert res.status_code == 401
    getattr(service, escritura).assert_not_called()


@pytest.mark.parametrize("rol", ["administrador", "planillero"])
@pytest.mark.parametrize("ruta, lectura, _respuesta", LECTURAS)
def test_usuarios_registrados_pueden_consultar(client, service, rol, ruta, lectura, _respuesta):
    res = client.get(ruta, headers=headers_de(rol))

    assert res.status_code == 200
    getattr(service, lectura).assert_called_once()


@pytest.mark.parametrize("ruta, lectura, _respuesta", LECTURAS)
def test_sin_token_no_puede_consultar(client, service, ruta, lectura, _respuesta):
    res = client.get(ruta)

    assert res.status_code == 401
    getattr(service, lectura).assert_not_called()
