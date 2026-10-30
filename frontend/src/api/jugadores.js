import { api, query } from "./client";

export const listarJugadores = ({ q, idFacultad, tipo } = {}) =>
  api.get(`/jugadores${query({ q, id_facultad: idFacultad, tipo })}`);
export const obtenerJugador = (ci) => api.get(`/jugadores/${ci}`);
