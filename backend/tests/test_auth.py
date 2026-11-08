import bcrypt
import jwt
import pytest

from app.config import settings
from app.routers import auth as auth_router

CORREO = "admin@ucu.edu.uy"
CONTRASENA = "Admin2026!"
# Pocas rondas para que los tests sean rápidos; el costo no cambia lo que se verifica.
HASH = bcrypt.hashpw(CONTRASENA.encode(), bcrypt.gensalt(rounds=4)).decode()


@pytest.fixture
def usuario_registrado(monkeypatch):
    def obtener_usuario(correo, conn):
        return {"contrasena": HASH, "rol": "administrador"} if correo == CORREO else None

    monkeypatch.setattr(auth_router.repo, "obtener_usuario", obtener_usuario)


def login(client, correo, contrasena):
    return client.post("/auth/login", json={"correo": correo, "contrasena": contrasena})


# ---------------------------------------------------------------- login
def test_login_correcto_devuelve_token_con_el_rol(client, usuario_registrado):
    res = login(client, CORREO, CONTRASENA)

    assert res.status_code == 200
    assert res.json()["rol"] == "administrador"
    payload = jwt.decode(res.json()["access_token"], settings.jwt_secret, algorithms=["HS256"])
    assert payload["sub"] == CORREO
    assert payload["rol"] == "administrador"


def test_login_no_devuelve_la_contrasena_ni_el_hash(client, usuario_registrado):
    cuerpo = login(client, CORREO, CONTRASENA).text

    assert CONTRASENA not in cuerpo
    assert HASH not in cuerpo


def test_contrasena_incorrecta_da_401(client, usuario_registrado):
    assert login(client, CORREO, "incorrecta").status_code == 401


def test_correo_inexistente_da_401(client, usuario_registrado):
    assert login(client, "nadie@ucu.edu.uy", CONTRASENA).status_code == 401


def test_el_error_no_revela_si_el_correo_existe(client, usuario_registrado):
    contrasena_mal = login(client, CORREO, "incorrecta").json()
    correo_mal = login(client, "nadie@ucu.edu.uy", "incorrecta").json()

    assert contrasena_mal == correo_mal


@pytest.mark.parametrize(
    "cuerpo", [{}, {"correo": CORREO}, {"contrasena": CONTRASENA}], ids=["vacio", "sin_contrasena", "sin_correo"]
)
def test_login_con_campos_faltantes_da_422(client, usuario_registrado, cuerpo):
    assert client.post("/auth/login", json=cuerpo).status_code == 422


# ---------------------------------------------------------------- /auth/me
def test_me_con_el_token_del_login_devuelve_el_usuario(client, usuario_registrado):
    token = login(client, CORREO, CONTRASENA).json()["access_token"]

    res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 200
    assert res.json() == {"correo": CORREO, "rol": "administrador"}


def test_me_sin_token_da_401(client_anonimo):
    assert client_anonimo.get("/auth/me").status_code == 401
