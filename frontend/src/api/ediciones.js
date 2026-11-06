import { api } from "./client";

export const listarEdiciones = () => api.get("/torneos");
export const obtenerEdicion = (id) => api.get(`/torneos/${id}`);
export const crearEdicion = (datos) => api.post("/torneos", datos);
export const cambiarEstadoEdicion = (id, estado) => api.patch(`/torneos/${id}/estado`, { estado });