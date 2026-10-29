from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = "db"
    db_port: int = 3306
    db_name: str = "torneo_db"

    db_admin_user: str
    db_admin_password: str
    db_planillero_user: str
    db_planillero_password: str
    db_login_user: str
    db_login_password: str

settings = Settings()