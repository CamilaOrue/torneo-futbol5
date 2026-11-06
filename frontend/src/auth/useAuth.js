import { createContext, useContext } from "react";

export const AuthContext = createContext(null);

/** Devuelve { usuario, rol, esAdmin, esPlanillero, cargando, login, logout }. */
export const useAuth = () => useContext(AuthContext);
