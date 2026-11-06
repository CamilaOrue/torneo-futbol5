from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.database import get_connection

_ALGORITMO = "HS256"
_bearer = HTTPBearer(auto_error=False)


def crear_token(correo: str, rol: str) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": correo,
        "rol": rol,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=settings.jwt_expira_minutos),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=_ALGORITMO)


def get_usuario_actual(credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> dict:
    if credenciales is None:
        raise HTTPException(401, "No autenticado")
    try:
        payload = jwt.decode(credenciales.credentials, settings.jwt_secret, algorithms=[_ALGORITMO])
    except jwt.InvalidTokenError as e:
        raise HTTPException(401, "Sesión inválida o vencida") from e
    return {"correo": payload["sub"], "rol": payload["rol"]}


def requiere_rol(*roles: str):
    def verificar(usuario: dict = Depends(get_usuario_actual)) -> dict:
        if usuario["rol"] not in roles:
            raise HTTPException(403, "No tenés permisos para esta acción")
        return usuario

    return verificar


def get_db_segun_rol(usuario: dict = Depends(get_usuario_actual)):
    conn = get_connection(usuario["rol"])
    try:
        yield conn
    finally:
        conn.close()
