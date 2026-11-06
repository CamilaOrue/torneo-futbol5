import { Navigate, useLocation } from "react-router-dom";
import { ANONIMO, inicioPara } from "./permisos";
import { useAuth } from "./useAuth";

/**
 * Renderiza `children` solo si el rol actual está en `roles`.
 * Sin sesión → al login; con sesión pero sin permiso → a su página de inicio.
 */
export default function RutaProtegida({ roles, children }) {
  const { rol, cargando } = useAuth();
  const location = useLocation();

  if (cargando) return null;
  if (roles.includes(rol ?? ANONIMO)) return children;
  if (!rol) return <Navigate to="/login" replace state={{ desde: location.pathname }} />;
  return <Navigate to={inicioPara(rol)} replace />;
}

/** Redirige a la página de inicio que corresponde al rol actual. */
export function Inicio() {
  const { rol, cargando } = useAuth();
  if (cargando) return null;
  return <Navigate to={inicioPara(rol)} replace />;
}
