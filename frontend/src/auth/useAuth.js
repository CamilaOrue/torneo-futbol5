import { createContext, useContext } from "react";

export const AuthContext = createContext(null);

/** Devuelve { usuario, esAdmin, login, logout }. */
export const useAuth = () => useContext(AuthContext);
