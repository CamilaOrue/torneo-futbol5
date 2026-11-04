import { api, query } from "./client";

export const listarJugadores = ({ q, idFacultad, tipo } = {}) =>
  api.get(`/jugadores${query({ q, id_facultad: idFacultad, tipo })}`);
export const obtenerJugador = (ci) => api.get(`/jugadores/${ci}`);
export const crearJugador = (datos) => api.post("/jugadores", datos);
export const actualizarJugador = (ci, datos) => api.put(`/jugadores/${ci}`, datos);
export const eliminarJugador = (ci) => api.delete(`/jugadores/${ci}`);
