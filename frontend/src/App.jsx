import { Route, Routes } from "react-router-dom";
import RutaProtegida, { Inicio } from "./auth/RutaProtegida";
import { SECCIONES } from "./auth/permisos";
import Layout from "./components/Layout";
import Ediciones from "./pages/Ediciones";
import Equipos from "./pages/Equipos";
import Jugadores from "./pages/Jugadores";
import Reportes from "./pages/Reportes";
import Login from "./pages/Login";
import Planilla from "./pages/Planilla";
import Partidos from "./pages/Partidos";
import Sanciones from "./pages/Sanciones";

const PAGINAS = {
  "/ediciones": <Ediciones />,
  "/equipos": <Equipos />,
  "/jugadores": <Jugadores />,
  "/reportes": <Reportes />,
  "/planilla": <Planilla />,
  "/partidos": <Partidos />,
  "/sanciones": <Sanciones />,
};

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Inicio />} />
        <Route path="login" element={<Login />} />
        {SECCIONES.map((s) => (
          <Route
            key={s.to}
            path={s.to.slice(1)}
            element={<RutaProtegida roles={s.roles}>{PAGINAS[s.to]}</RutaProtegida>}
          />
        ))}
        <Route path="*" element={<Inicio />} />
      </Route>
    </Routes>
  );
}
