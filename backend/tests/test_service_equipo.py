"""Tests del service de equipo: reglas del plantel.

No usan la base de datos: se reemplazan las funciones del repositorio
por versiones falsas que devuelven el equipo y el plantel de cada caso.
"""

import pytest

from app.services import equipo as service

ID_FACULTAD = 1


def jugador(tipo="grado", id_facultad=ID_FACULTAD):
    return {"tipo": tipo, "id_facultad": id_facultad}


@pytest.fixture
def cargar(monkeypatch):
    """Configura qué devuelve el repositorio para el equipo que se valida."""

    def _cargar(plantel, equipo={"id_facultad": ID_FACULTAD}):
        monkeypatch.setattr(service.repo, "obtener", lambda conn, id_equipo: equipo)
        monkeypatch.setattr(service.repo, "plantel", lambda conn, id_equipo: plantel)

    return _cargar


# ----------------------------------------------------------- equipo_valido

def test_equipo_valido_no_lanza_error(cargar):
    cargar([jugador()] * 5)
    service.equipo_valido(conn=None, id_equipo=1)


def test_equipo_inexistente(cargar):
    cargar([], equipo=None)
    with pytest.raises(ValueError, match="El equipo no existe"):
        service.equipo_valido(conn=None, id_equipo=99)


@pytest.mark.parametrize("cantidad", [0, 4, 11])
def test_cantidad_de_jugadores_invalida(cargar, cantidad):
    cargar([jugador()] * cantidad)
    with pytest.raises(ValueError, match="entre 5 y 10 jugadores"):
        service.equipo_valido(conn=None, id_equipo=1)


def test_mas_de_dos_funcionarios(cargar):
    cargar([jugador()] * 3 + [jugador("docente"), jugador("funcionario"), jugador("docente")])
    with pytest.raises(ValueError, match="como máximo 2 funcionarios"):
        service.equipo_valido(conn=None, id_equipo=1)


def test_jugador_de_otra_facultad(cargar):
    cargar([jugador()] * 4 + [jugador(id_facultad=2)])
    with pytest.raises(ValueError, match="misma facultad"):
        service.equipo_valido(conn=None, id_equipo=1)


def test_se_valida_cantidad_antes_que_funcionarios(cargar):
    # 3 funcionarios y solo 3 jugadores: se informa primero la cantidad.
    cargar([jugador("funcionario")] * 3)
    with pytest.raises(ValueError, match="entre 5 y 10 jugadores"):
        service.equipo_valido(conn=None, id_equipo=1)


# ------------------------------------------------- tiene_entre_5_y_10_jugadores

@pytest.mark.parametrize("cantidad, esperado", [
    (4, False),
    (5, True),
    (7, True),
    (10, True),
    (11, False),
])
def test_tiene_entre_5_y_10_jugadores(cantidad, esperado):
    assert service.tiene_entre_5_y_10_jugadores([jugador()] * cantidad) is esperado


# ---------------------------------------------------- maximo_dos_funcionarios

@pytest.mark.parametrize("tipos, esperado", [
    (["grado"] * 5, True),
    (["grado", "posgrado"] * 3, True),
    (["funcionario", "funcionario"], True),
    (["docente", "funcionario"], True),
    (["docente", "docente", "docente"], False),
    (["docente", "funcionario", "funcionario"], False),
])
def test_maximo_dos_funcionarios(tipos, esperado):
    plantel = [jugador(tipo) for tipo in tipos]
    assert service.maximo_dos_funcionarios(plantel) is esperado


# ------------------------------------------- todos_pertenecen_a_misma_facultad

def test_todos_de_la_misma_facultad():
    plantel = [jugador()] * 5
    assert service.todos_pertenecen_a_misma_facultad(plantel, ID_FACULTAD) is True


def test_uno_de_otra_facultad():
    plantel = [jugador()] * 4 + [jugador(id_facultad=3)]
    assert service.todos_pertenecen_a_misma_facultad(plantel, ID_FACULTAD) is False
