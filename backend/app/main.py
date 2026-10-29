from fastapi import FastAPI

from app.routers import health

app = FastAPI(title="Torneo Interfacultades de Fútbol 5")

app.include_router(health.router)