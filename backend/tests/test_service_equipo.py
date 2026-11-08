"""Tests del service de equipo: reglas del plantel (validar_plantel_completo).

No usan la base de datos: se reemplazan las funciones del repositorio
por versiones falsas que devuelven el equipo y el plantel de cada caso.
"""

import pytest
from fastapi import HTTPException

from app.services import equipo as service

ID_FACULTAD = 1
EQUIPO = {"nombre": "Ingeniería FC", "id_facultad": ID_FACULTAD}


def jugador(tipo="grado", id_facultad=ID_FACULTAD):
    return {"tipo": tipo, "id_facultad": id_facultad}


@pytest.fixture
def cargar(monkeypatch):
    """Configura qué devuelve el repositorio para el equipo que se valida."""

    def _cargar(plantel, equipo=EQUIPO):
        monkeypatch.setattr(service.repo, "obtener", lambda conn, id_equipo: equipo)
        monkeypatch.setattr(service.repo, "plantel", lambda conn, id_equipo: plantel)

    return _cargar


def validar(id_equipo=1):
    service.validar_plantel_completo(conn=None, id_equipo=id_equipo)


def test_plantel_valido_no_lanza_error(cargar):
    cargar([jugador()] * 5)
    validar()


def test_equipo_inexistente_da_404(cargar):
    cargar([], equipo=None)
    with pytest.raises(HTTPException) as error:
        validar(id_equipo=99)
    assert error.value.status_code == 404
    assert "El equipo no existe" in error.value.detail


# ----------------------------------------------------------- entre 5 y 10 jugadores

@pytest.mark.parametrize("cantidad", [5, 7, 10])
def test_cantidad_de_jugadores_valida(cargar, cantidad):
    cargar([jugador()] * cantidad)
    validar()


@pytest.mark.parametrize("cantidad", [0, 4, 11])
def test_cantidad_de_jugadores_invalida(cargar, cantidad):
    cargar([jugador()] * cantidad)
    with pytest.raises(HTTPException) as error:
        validar()
    assert error.value.status_code == 400
    assert "entre 5 y 10 jugadores" in error.value.detail


# ----------------------------------------------------- máximo 2 docentes/funcionarios

@pytest.mark.parametrize("externos", [
    [],
    ["docente"],
    ["funcionario", "funcionario"],
    ["docente", "funcionario"],
])
def test_hasta_dos_docentes_o_funcionarios(cargar, externos):
    cargar([jugador()] * (5 - len(externos)) + [jugador(tipo) for tipo in externos])
    validar()


@pytest.mark.parametrize("externos", [
    ["docente", "docente", "docente"],
    ["docente", "funcionario", "funcionario"],
])
def test_mas_de_dos_docentes_o_funcionarios(cargar, externos):
    cargar([jugador()] * 3 + [jugador(tipo) for tipo in externos])
    with pytest.raises(HTTPException) as error:
        validar()
    assert error.value.status_code == 400
    assert "máximo de 2 docentes/funcionarios" in error.value.detail


def test_posgrado_no_cuenta_como_externo(cargar):
    cargar([jugador("posgrado")] * 6)
    validar()


# ------------------------------------------------------------------- misma facultad

def test_jugador_de_otra_facultad(cargar):
    cargar([jugador()] * 4 + [jugador(id_facultad=2)])
    with pytest.raises(HTTPException) as error:
        validar()
    assert error.value.status_code == 400
    assert "facultad del equipo" in error.value.detail


# --------------------------------------------------------------- orden de las reglas

def test_se_valida_cantidad_antes_que_externos(cargar):
    # 3 funcionarios y solo 3 jugadores: se informa primero la cantidad.
    cargar([jugador("funcionario")] * 3)
    with pytest.raises(HTTPException) as error:
        validar()
    assert "entre 5 y 10 jugadores" in error.value.detail


def test_se_valida_externos_antes_que_facultad(cargar):
    # 3 docentes de otra facultad: se informa primero el cupo de externos.
    cargar([jugador()] * 2 + [jugador("docente", id_facultad=2)] * 3)
    with pytest.raises(HTTPException) as error:
        validar()
    assert "máximo de 2 docentes/funcionarios" in error.value.detail
