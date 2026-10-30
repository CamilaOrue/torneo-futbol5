import { api, query } from "./client";

export const listarEquipos = (idTorneo) =>
  api.get(`/equipos${query({ id_torneo: idTorneo })}`);
export const obtenerEquipo = (id) => api.get(`/equipos/${id}`);
