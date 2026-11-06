import base64
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app import security
from app.config import settings
from app.security import crear_token, get_db_segun_rol, get_usuario_actual, requiere_rol

api = FastAPI()


@api.get("/usuario")
def ver_usuario(usuario=Depends(get_usuario_actual)):
    return usuario


@api.get("/solo-admin", dependencies=[Depends(requiere_rol("administrador"))])
def solo_admin():
    return {"ok": True}


@api.get("/dos-roles", dependencies=[Depends(requiere_rol("administrador", "planillero"))])
def dos_roles():
    return {"ok": True}


@api.get("/conexion")
def ver_conexion(conn=Depends(get_db_segun_rol)):
    return {"ok": True}


client = TestClient(api)


def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def b64(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).rstrip(b"=").decode()


# ---------------------------------------------------------------- crear_token
def test_el_token_lleva_correo_rol_y_vencimiento():
    token = crear_token("admin@ucu.edu.uy", "administrador")

    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])

    assert payload["sub"] == "admin@ucu.edu.uy"
    assert payload["rol"] == "administrador"
    assert payload["exp"] - payload["iat"] == settings.jwt_expira_minutos * 60


# ---------------------------------------------------------------- get_usuario_actual
def test_token_valido_devuelve_el_usuario():
    res = client.get("/usuario", headers=bearer(crear_token("p@ucu.edu.uy", "planillero")))

    assert res.status_code == 200
    assert res.json() == {"correo": "p@ucu.edu.uy", "rol": "planillero"}


def test_sin_token_da_401():
    assert client.get("/usuario").status_code == 401


def test_token_mal_formado_da_401():
    assert client.get("/usuario", headers=bearer("no-es-un-jwt")).status_code == 401


def test_token_vencido_da_401():
    vencimiento = datetime.now(timezone.utc) - timedelta(minutes=1)
    token = jwt.encode(
        {"sub": "a@ucu.edu.uy", "rol": "administrador", "exp": vencimiento},
        settings.jwt_secret,
        algorithm="HS256",
    )

    assert client.get("/usuario", headers=bearer(token)).status_code == 401


def test_token_firmado_con_otra_clave_da_401():
    token = jwt.encode(
        {"sub": "a@ucu.edu.uy", "rol": "administrador"}, "otra-clave-" + "y" * 32, algorithm="HS256"
    )

    assert client.get("/usuario", headers=bearer(token)).status_code == 401


def test_token_sin_firma_da_401():
    token = jwt.encode({"sub": "a@ucu.edu.uy", "rol": "administrador"}, None, algorithm="none")

    assert client.get("/usuario", headers=bearer(token)).status_code == 401


# ---------------------------------------------------------------- requiere_rol
@pytest.mark.parametrize(
    "ruta, rol, esperado",
    [
        ("/solo-admin", "administrador", 200),
        ("/solo-admin", "planillero", 403),
        ("/solo-admin", "desconocido", 403),
        ("/dos-roles", "administrador", 200),
        ("/dos-roles", "planillero", 200),
        ("/dos-roles", "desconocido", 403),
    ],
)
def test_requiere_rol(ruta, rol, esperado):
    res = client.get(ruta, headers=bearer(crear_token("u@ucu.edu.uy", rol)))

    assert res.status_code == esperado


@pytest.mark.parametrize("ruta", ["/solo-admin", "/dos-roles"])
def test_requiere_rol_sin_token_da_401(ruta):
    assert client.get(ruta).status_code == 401


# ---------------------------------------------------------------- get_db_segun_rol
@pytest.mark.parametrize("rol", ["administrador", "planillero"])
def test_la_conexion_corresponde_al_rol_y_se_cierra(monkeypatch, rol):
    conexion = MagicMock()
    get_connection = MagicMock(return_value=conexion)
    monkeypatch.setattr(security, "get_connection", get_connection)

    res = client.get("/conexion", headers=bearer(crear_token("u@ucu.edu.uy", rol)))

    assert res.status_code == 200
    get_connection.assert_called_once_with(rol)
    conexion.close.assert_called_once()


def test_sin_token_no_se_abre_ninguna_conexion(monkeypatch):
    get_connection = MagicMock()
    monkeypatch.setattr(security, "get_connection", get_connection)

    assert client.get("/conexion").status_code == 401
    get_connection.assert_not_called()
