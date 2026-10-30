from fastapi import APIRouter, Depends

from app.database import get_db_admin

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/health/db")
def health_db(conn=Depends(get_db_admin)):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 AS ok")
        return {"db": cur.fetchone()["ok"] == 1}
