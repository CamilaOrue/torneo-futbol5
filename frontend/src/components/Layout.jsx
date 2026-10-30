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
        <h1>Torneo Interfacultades de Fútbol 5</h1>
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
      </header>
      <main className="contenido">
        <Outlet />
      </main>
    </div>
  );
}
