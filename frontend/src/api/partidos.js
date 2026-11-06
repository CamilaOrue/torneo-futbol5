import { api, query } from "./client";

export const listarPartidos = (idTorneo) => api.get(`/partidos/${query({ id_torneo: idTorneo })}`);
export const crearPartido = (datos) => api.post("/partidos/", datos);
export const cambiarEstadoPartido = (idPartido, estado) => api.patch(`/partidos/${idPartido}/estado`, { estado });
export const eliminarPartido = (idPartido) => api.delete(`/partidos/${idPartido}`);
export const listarCanchas = () => api.get("/canchas");
export const modificarPartido = (idPartido, datos) => api.put(`/partidos/${idPartido}`, datos);