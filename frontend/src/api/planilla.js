import { api } from "./client";

export const guardarPlanilla = (idPartido, datos) => api.put(`/planillas/${idPartido}`, datos);
export const guardarGoles = (idPartido, datos) => api.post(`/goles/partido/${idPartido}`, datos);
export const guardarTarjeta = (idPartido, datos) => api.post(`/tarjetas/partido/${idPartido}`, datos);
export const eliminarGol = (idGol) => api.delete(`/goles/${idGol}`);