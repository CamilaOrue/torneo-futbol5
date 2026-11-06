import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Ediciones from "./pages/Ediciones";
import Equipos from "./pages/Equipos";
import Jugadores from "./pages/Jugadores";
import Reportes from "./pages/Reportes";
import Login from "./pages/Login";
import Planilla from "./pages/Planilla";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/ediciones" replace />} />
        <Route path="ediciones" element={<Ediciones />} />
        <Route path="equipos" element={<Equipos />} />
        <Route path="jugadores" element={<Jugadores />} />
        <Route path="reportes" element={<Reportes />} />
        <Route path="login" element={<Login />} />
        <Route path="*" element={<Navigate to="/ediciones" replace />} />
        <Route path="planilla" element={<Planilla />} />
      </Route>
    </Routes>
  );
}
