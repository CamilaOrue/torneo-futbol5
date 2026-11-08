import { api, query } from "./client";

export const listarComplejos = ({ q } = {}) => api.get(`/complejos${query({ q })}`);
export const crearComplejo = (datos) => api.post("/complejos", datos);
export const actualizarComplejo = (id, datos) => api.put(`/complejos/${id}`, datos);
export const eliminarComplejo = (id) => api.delete(`/complejos/${id}`);

const rutaCancha = (idComplejo, nombre) => `/canchas/${idComplejo}/${encodeURIComponent(nombre)}`;

export const listarCanchasDe = (idComplejo) => api.get(`/canchas${query({ id_complejo: idComplejo })}`);
export const crearCancha = (idComplejo, datos) => api.post(`/canchas/${idComplejo}`, datos);
export const actualizarCancha = (idComplejo, nombre, datos) => api.put(rutaCancha(idComplejo, nombre), datos);
export const eliminarCancha = (idComplejo, nombre) => api.delete(rutaCancha(idComplejo, nombre));
