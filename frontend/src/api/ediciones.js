import { api } from "./client";

export const listarEdiciones = () => api.get("/torneos");
export const obtenerEdicion = (id) => api.get(`/torneos/${id}`);
