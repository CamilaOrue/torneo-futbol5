import sys
from pathlib import Path

# Garantiza que /code esté en la ruta de Python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    # TestClient es la forma nativa y sincrónica de probar FastAPI
    with TestClient(app) as c:
        yield c