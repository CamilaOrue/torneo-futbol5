import { Link, NavLink, Outlet } from "react-router-dom";
import { seccionesPara } from "../auth/permisos";
import { useAuth } from "../auth/useAuth";

export default function Layout() {
  const { usuario, rol, logout } = useAuth();

  return (
    <div className="app">
      <header className="cabecera">
        <div className="cabecera-interior">
          <div className="marca">
            <img src="/favicon.svg" alt="" width="40" height="40" />
            <div>
              <p className="marca-kicker">UCU · Fútbol 5</p>
              <h1>Torneo Interfacultades</h1>
            </div>
            <div className="sesion">
              {usuario ? (
                <>
                  <span>{usuario.correo}</span>
                  <button className="link" onClick={logout}>
                    Salir
                  </button>
                </>
              ) : (
                <Link to="/login">Ingresar</Link>
              )}
            </div>
          </div>
          <nav className="tabs" aria-label="Secciones">
            {seccionesPara(rol).map((t) => (
              <NavLink
                key={t.to}
                to={t.to}
                className={({ isActive }) => "tab" + (isActive ? " activa" : "")}
              >
                {t.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="contenido">
        <Outlet />
      </main>
    </div>
  );
}
