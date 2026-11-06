import { api } from "./client";

export const iniciarSesion = (correo, contrasena) => api.post("/auth/login", { correo, contrasena });
export const obtenerSesion = () => api.get("/auth/me");
