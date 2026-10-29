import pymysql
from pymysql.cursors import DictCursor

from app.config import settings

_CREDENCIALES = {
    "administrador": (settings.db_admin_user, settings.db_admin_password),
    "planillero": (settings.db_planillero_user, settings.db_planillero_password),
    "login": (settings.db_login_user, settings.db_login_password),
}


def get_connection(rol: str = "administrador"):
    user, password = _CREDENCIALES[rol]
    return pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=user,
        password=password,
        database=settings.db_name,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
    )


def get_db_admin():
    """Dependencia FastAPI: conexión con el usuario administrador."""
    conn = get_connection("administrador")
    try:
        yield conn
    finally:
        conn.close()


def get_db_planillero():
    """Dependencia FastAPI: conexión con el usuario planillero."""
    conn = get_connection("planillero")
    try:
        yield conn
    finally:
        conn.close()