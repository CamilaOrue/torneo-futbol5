from fastapi import FastAPI

from app.routers import equipos, facultades, health, jugadores, torneos, planteles, complejos, canchas, partidos, planillas, goles, tarjetas, sanciones

app = FastAPI(title="Torneo Interfacultades de Fútbol 5")

app.include_router(health.router)
app.include_router(torneos.router)
app.include_router(equipos.router)
app.include_router(jugadores.router)
app.include_router(facultades.router)
app.include_router(planteles.router)
app.include_router(complejos.router)
app.include_router(canchas.router)
app.include_router(partidos.router)
app.include_router(planillas.router)
app.include_router(goles.router)
app.include_router(tarjetas.router)
app.include_router(sanciones.router)