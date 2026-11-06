import { api, query } from "./client";

export const listarEquipos = (idTorneo) =>
  api.get(`/equipos${query({ id_torneo: idTorneo })}`);
export const obtenerEquipo = (id) => api.get(`/equipos/${id}`);
export const crearEquipo = (equipo) => api.post("/equipos", equipo);
export const actualizarEquipo = (id, equipo) => api.put(`/equipos/${id}`, equipo);
export const eliminarEquipo = (id) => api.delete(`/equipos/${id}`);

export const quitarDelPlantel = (idEquipo, ci) => api.delete(`/equipos/${idEquipo}/plantel/${ci}`);
export const jugadoresDisponibles = (idEquipo) => api.get(`/equipos/${idEquipo}/plantel/disponibles`);
export const agregarAlPlantel = (idEquipo, integrante) =>
  api.post(`/equipos/${idEquipo}/plantel`, integrante);
