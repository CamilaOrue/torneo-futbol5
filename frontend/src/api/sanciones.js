import { api, query } from "./client";

export const listarSanciones = (idTorneo) => api.get(`/sanciones/${query({ id_torneo: idTorneo })}`);
export const crearSancion = (datos) => api.post("/sanciones/", datos);
export const modificarSancion = (idSancion, datos) => api.put(`/sanciones/${idSancion}`, datos);
export const eliminarSancion = (idSancion) => api.delete(`/sanciones/${idSancion}`);