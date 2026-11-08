import os
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

_VALORES_DE_PRUEBA = dict(
    DB_HOST="mysql-no-disponible-en-tests",
    DB_ADMIN_USER="test",
    DB_ADMIN_PASSWORD="test",
    DB_PLANILLERO_USER="test",
    DB_PLANILLERO_PASSWORD="test",
    DB_LOGIN_USER="test",
    DB_LOGIN_PASSWORD="test",
    JWT_SECRET="clave-solo-para-tests-" + "x" * 32,
)
for _clave, _valor in _VALORES_DE_PRUEBA.items():
    os.environ.setdefault(_clave, _valor)

from app.main import app
from app.database import get_db_admin, get_db_login, get_db_planillero
from app.security import crear_token, get_db_segun_rol


def _conexion_falsa():
    yield MagicMock()


def _poner_bd_falsa():
    app.dependency_overrides[get_db_admin] = _conexion_falsa
    app.dependency_overrides[get_db_login] = _conexion_falsa
    app.dependency_overrides[get_db_planillero] = _conexion_falsa
    app.dependency_overrides[get_db_segun_rol] = _conexion_falsa


def _header_admin() -> dict:
    return {"Authorization": f"Bearer {crear_token('admin@ucu.edu.uy', 'administrador')}"}


@pytest.fixture
def client():
    """BD falsa + token de administrador por defecto en cada request.

    Es el cliente de la mayoría de los tests (unitarios con mocks).
    Los tests que pasan su propio header (headers_de) lo pisan sin problema.
    """
    _poner_bd_falsa()
    with TestClient(app, headers=_header_admin()) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_sin_login():
    """BD falsa y SIN token: para los tests que esperan 401."""
    _poner_bd_falsa()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_integracion():
    """Token de administrador y BD REAL (el MySQL del docker compose).

    Para los tests de complejos/canchas, que crean y borran datos de verdad.
    """
    app.dependency_overrides.clear()
    with TestClient(app, headers=_header_admin()) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def headers_de():
    """Devuelve el header Authorization de un usuario con el rol indicado."""

    def _headers(rol: str) -> dict:
        return {"Authorization": f"Bearer {crear_token(f'{rol}@ucu.edu.uy', rol)}"}

    return _headers