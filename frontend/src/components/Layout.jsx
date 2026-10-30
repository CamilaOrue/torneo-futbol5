import { NavLink, Outlet } from "react-router-dom";

const TABS = [
  { to: "/ediciones", label: "Ediciones" },
  { to: "/equipos", label: "Equipos" },
  { to: "/jugadores", label: "Jugadores" },
];

export default function Layout() {
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
          </div>
          <nav className="tabs" aria-label="Secciones">
            {TABS.map((t) => (
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
