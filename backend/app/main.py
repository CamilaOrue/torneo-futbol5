from fastapi import FastAPI

from app.routers import auth, equipos, facultades, health, jugadores, reportes, torneos

app = FastAPI(title="Torneo Interfacultades de Fútbol 5")

app.include_router(health.router)
app.include_router(torneos.router)
app.include_router(equipos.router)
app.include_router(jugadores.router)
app.include_router(facultades.router)
app.include_router(reportes.router)
app.include_router(auth.router)
