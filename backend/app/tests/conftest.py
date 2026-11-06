import sys
from pathlib import Path

# Garantiza que /code esté en la ruta de Python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.security import get_usuario_actual


@pytest.fixture
def client():
    # los tests de integración entran como administrador
    app.dependency_overrides[get_usuario_actual] = lambda: {
        "correo": "admin@ucu.edu.uy",
        "rol": "administrador",
    }
    # TestClient es la forma nativa y sincrónica de probar FastAPI
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_usuario_actual, None)
