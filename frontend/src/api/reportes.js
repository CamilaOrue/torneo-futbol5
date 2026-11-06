import { api, query } from "./client";

export const jugadoresPorFacultad = () => api.get("/reportes/jugadores-por-facultad");
export const porcentajePorEstados = () => api.get("/reportes/porcentaje-por-estados");
export const cantidadSanciones = () => api.get("/reportes/cantidad-sanciones");
export const canchasUsadas = () => api.get("/reportes/canchas-usadas");
export const turnosUsados = () => api.get("/reportes/turnos-usados");
export const topJugadores = () => api.get("/reportes/top-jugadores");
export const jugadoresNoPlanilla = () => api.get("/reportes/jugadores-no-planilla");
export const fairPlay = () => api.get("/reportes/fair-play");

export const promedioGolesPartidoFecha = (idTorneo) =>
  api.get(`/reportes/promedio-goles-partido-fecha${query({ id_torneo: idTorneo })}`);

export const promedioGolesPartidoEdicion = (idTorneo) =>
  api.get(`/reportes/promedio-goles-partido-edicion${query({ id_torneo: idTorneo })}`);

export const tablaPosiciones = (idTorneo) =>
  api.get(`/reportes/tabla-posiciones${query({ id_torneo: idTorneo })}`);

export const edadPromedioPlantel = (idTorneo) =>
  api.get(`/reportes/edad-promedio-plantel${query({ id_torneo: idTorneo })}`);

export const partidosJugadosPorComplejo = (idTorneo) =>
  api.get(`/reportes/partidos-jugados-por-complejo${query({ id_torneo: idTorneo })}`);

export const golesPorFacultad = (idTorneo) =>
  api.get(`/reportes/goles-por-facultad${query({ id_torneo: idTorneo })}`);