import { api } from "./client";


export const guardarPlanilla = (idPartido, datos) => api.post(`/planilla/${idPartido}/jugadores`, datos);
export const guardarGoles = (idPartido, datos) => api.post(`/planilla/${idPartido}/goles`, datos);
export const guardarTarjeta = (idPartido, datos) => api.post(`/planilla/${idPartido}/tarjetas`, datos);