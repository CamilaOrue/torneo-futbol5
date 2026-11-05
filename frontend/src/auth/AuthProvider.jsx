import { useEffect, useState } from "react";
import { iniciarSesion, obtenerSesion } from "../api/auth";
import { AuthContext } from "./useAuth";

/** Mantiene la sesión. El token queda en localStorage y `api/client.js` lo manda en cada request. */
export default function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);

  // Al recargar la página, recupera el usuario a partir del token guardado
  useEffect(() => {
    if (!localStorage.getItem("token")) return;
    obtenerSesion()
      .then(setUsuario)
      .catch(() => {});
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

  const esAdmin = usuario?.rol === "administrador";

  return (
    <AuthContext.Provider value={{ usuario, esAdmin, login, logout }}>{children}</AuthContext.Provider>
  );
}
