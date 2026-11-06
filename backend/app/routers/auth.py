from fastapi import APIRouter, Depends, HTTPException
from app.schemas.auth import LoginRequest
from app.database import get_db_login
from app.repositories import auth as repo
import bcrypt
from app.security import crear_token, get_usuario_actual

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(login_request: LoginRequest, conn=Depends(get_db_login)):
    """Autentica a un usuario y devuelve un token de acceso."""
    user = repo.obtener_usuario(login_request.correo, conn)
    if not user:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    valid_password = bcrypt.checkpw(login_request.contrasena.encode("utf-8"), user["contrasena"].encode("utf-8"))
    if not valid_password:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    token = crear_token(login_request.correo, user["rol"])
    return {"access_token": token, "rol": user["rol"]}


@router.get("/me")
def me(usuario: dict = Depends(get_usuario_actual)):
    return usuario
