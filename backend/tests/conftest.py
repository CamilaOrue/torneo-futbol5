import os

os.environ.update(
    DB_HOST="mysql-no-disponible-en-tests",
    DB_ADMIN_USER="test",
    DB_ADMIN_PASSWORD="test",
    DB_PLANILLERO_USER="test",
    DB_PLANILLERO_PASSWORD="test",
    DB_LOGIN_USER="test",
    DB_LOGIN_PASSWORD="test",
    JWT_SECRET="clave-solo-para-tests-" + "x" * 32,
)

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.database import get_db_admin, get_db_login
from app.main import app
from app.security import crear_token


@pytest.fixture
def client():
    def conexion_falsa():
        yield MagicMock()

    app.dependency_overrides[get_db_admin] = conexion_falsa
    app.dependency_overrides[get_db_login] = conexion_falsa
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def headers_de():
    """Devuelve el header Authorization de un usuario con el rol indicado."""

    def _headers(rol: str) -> dict:
        return {"Authorization": f"Bearer {crear_token(f'{rol}@ucu.edu.uy', rol)}"}

    return _headers
