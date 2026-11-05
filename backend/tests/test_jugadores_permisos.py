from unittest.mock import MagicMock

import pytest

from app.routers import jugadores as jugadores_router

DATOS = {
    "nombre": "Ana",
    "apellido": "Pérez",
    "email": "ana.perez@ucu.edu.uy",
    "fecha_nacimiento": "2000-01-01",
    "id_facultad": 1,
    "tipo": "grado",
}

# (método, ruta, cuerpo, función del repositorio que escribe, status si tiene permiso)
OPERACIONES = [
    pytest.param("POST", "/jugadores", {"ci": "12345678", **DATOS}, "crear", 201, id="alta"),
    pytest.param("PUT", "/jugadores/12345678", DATOS, "actualizar", 200, id="modificacion"),
    pytest.param("DELETE", "/jugadores/12345678", None, "eliminar", 204, id="baja"),
]


@pytest.fixture
def repo(monkeypatch):
    falso = MagicMock()
    falso.existe_facultad.return_value = True
    falso.bloquear.return_value = {"tipo": "grado"}
    falso.planteles_de_otra_facultad.return_value = []
    falso.obtener.return_value = {
        "ci": "12345678",
        **DATOS,
        "facultad": "Ingeniería",
        "equipo_actual": None,
    }
    monkeypatch.setattr(jugadores_router, "repo", falso)
    return falso


@pytest.mark.parametrize("metodo, ruta, cuerpo, escritura, esperado", OPERACIONES)
def test_administrador_puede(client, repo, headers_de, metodo, ruta, cuerpo, escritura, esperado):
    res = client.request(metodo, ruta, json=cuerpo, headers=headers_de("administrador"))

    assert res.status_code == esperado
    getattr(repo, escritura).assert_called_once()


@pytest.mark.parametrize("metodo, ruta, cuerpo, escritura, esperado", OPERACIONES)
def test_planillero_recibe_403_y_no_escribe(client, repo, headers_de, metodo, ruta, cuerpo, escritura, esperado):
    res = client.request(metodo, ruta, json=cuerpo, headers=headers_de("planillero"))

    assert res.status_code == 403
    getattr(repo, escritura).assert_not_called()


@pytest.mark.parametrize("metodo, ruta, cuerpo, escritura, esperado", OPERACIONES)
def test_sin_token_recibe_401_y_no_escribe(client, repo, metodo, ruta, cuerpo, escritura, esperado):
    res = client.request(metodo, ruta, json=cuerpo)

    assert res.status_code == 401
    getattr(repo, escritura).assert_not_called()


@pytest.mark.parametrize("metodo, ruta, cuerpo, escritura, esperado", OPERACIONES)
def test_token_invalido_recibe_401_y_no_escribe(client, repo, metodo, ruta, cuerpo, escritura, esperado):
    res = client.request(metodo, ruta, json=cuerpo, headers={"Authorization": "Bearer no-es-un-jwt"})

    assert res.status_code == 401
    getattr(repo, escritura).assert_not_called()
