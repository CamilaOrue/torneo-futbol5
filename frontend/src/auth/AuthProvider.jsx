import { useEffect, useState } from "react";
import { iniciarSesion, obtenerSesion } from "../api/auth";
import { AuthContext } from "./useAuth";

/** Mantiene la sesión. El token queda en localStorage y `api/client.js` lo manda en cada request. */
export default function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  // Mientras se recupera la sesión guardada no se sabe el rol: las rutas protegidas esperan
  const [cargando, setCargando] = useState(() => Boolean(localStorage.getItem("token")));

  // Al recargar la página, recupera el usuario a partir del token guardado
  useEffect(() => {
    if (!localStorage.getItem("token")) return;
    obtenerSesion()
      .then(setUsuario)
      .catch(() => localStorage.removeItem("token"))
      .finally(() => setCargando(false));
  }, []);

  async function login(correo, contrasena) {
    const { access_token, rol } = await iniciarSesion(correo, contrasena);
    localStorage.setItem("token", access_token);
    setUsuario({ correo, rol });
  }

  function logout() {
    localStorage.removeItem("token");
    setUsuario(null);
  }

  const rol = usuario?.rol ?? null;
  const esAdmin = rol === "administrador";
  const esPlanillero = rol === "planillero";

  return (
    <AuthContext.Provider value={{ usuario, rol, esAdmin, esPlanillero, cargando, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
