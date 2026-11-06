import { api, query } from "./client";

export const listarEquipos = (idTorneo) =>
  api.get(`/equipos${query({ id_torneo: idTorneo })}`);
export const obtenerEquipo = (id) => api.get(`/equipos/${id}`);
export const crearEquipo = (equipo) => api.post("/equipos", equipo);
export const actualizarEquipo = (id, equipo) => api.put(`/equipos/${id}`, equipo);
export const eliminarEquipo = (id) => api.delete(`/equipos/${id}`);
