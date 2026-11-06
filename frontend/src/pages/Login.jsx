import { useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

export default function Login() {
  const { usuario, login } = useAuth();
  const location = useLocation();
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState(null);
  const [enviando, setEnviando] = useState(false);

  // Al iniciar sesión, `usuario` cambia y esta redirección vuelve a la página pedida
  // (o a la de inicio de su rol; si no tiene permiso, la ruta protegida lo reubica)
  if (usuario) return <Navigate to={location.state?.desde ?? "/"} replace />;

  async function enviar(ev) {
    ev.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await login(correo.trim(), contrasena);
    } catch (e) {
      setError(e.message);
      setEnviando(false);
    }
  }

  return (
    <section className="panel login">
      <h2>Iniciar sesión</h2>
      <form onSubmit={enviar} className="formulario">
        <div className="campo">
          <label htmlFor="login-correo">Correo</label>
          <input
            id="login-correo"
            type="email"
            maxLength={100}
            autoComplete="username"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            required
          />
        </div>
        <div className="campo">
          <label htmlFor="login-contrasena">Contraseña</label>
          <input
            id="login-contrasena"
            type="password"
            autoComplete="current-password"
            value={contrasena}
            onChange={(e) => setContrasena(e.target.value)}
            required
          />
        </div>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <div className="modal-acciones">
          <button type="submit" className="btn btn-primario" disabled={enviando}>
            {enviando ? "Ingresando…" : "Ingresar"}
          </button>
        </div>
      </form>
    </section>
  );
}
