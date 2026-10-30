import { api } from "./client";

export const listarFacultades = () => api.get("/facultades");
