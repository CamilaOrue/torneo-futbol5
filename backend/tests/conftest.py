import os
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

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

from app.main import app
from app.database import get_db_admin, get_db_login, get_db_planillero
from app.security import crear_token, get_db_segun_rol


@pytest.fixture
def client():
    def conexion_falsa():
        yield MagicMock()

    app.dependency_overrides[get_db_admin] = conexion_falsa
    app.dependency_overrides[get_db_login] = conexion_falsa
    app.dependency_overrides[get_db_planillero] = conexion_falsa
    app.dependency_overrides[get_db_segun_rol] = conexion_falsa

    # Inyectamos un token de administrador por defecto al TestClient.
    token_admin = crear_token("admin@ucu.edu.uy", "administrador")
    
    with TestClient(app, headers={"Authorization": f"Bearer {token_admin}"}) as c:
        yield c
    
    app.dependency_overrides.clear()


@pytest.fixture
def client_anonimo(client):
    """Igual que `client`, pero sin el token de administrador: para probar los 401."""
    client.headers.pop("Authorization", None)
    return client


@pytest.fixture
def headers_de():
    """Devuelve el header Authorization de un usuario con el rol indicado."""
    def _headers(rol: str) -> dict:
        return {"Authorization": f"Bearer {crear_token(f'{rol}@ucu.edu.uy', rol)}"}
    return _headers
