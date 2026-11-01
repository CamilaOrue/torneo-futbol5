import { useState } from "react";
import { listarEdiciones } from "../api/ediciones";
import { useFetch } from "../hooks/useFetch";
import Estado from "./Estado";
import { TablaReporte } from "./ReporteTabla";

export default function ReportePorEdicion({ titulo, pedirDatos, columnas, abierto = false }) {
  const ediciones = useFetch(listarEdiciones);
  const [idElegido, setIdElegido] = useState(null);

  return (
    <details className="reporte" open={abierto}>
      <summary>{titulo}</summary>
      <Estado {...ediciones}>
        {(lista) => {
          if (!lista.length) return <p className="vacio">No hay ediciones cargadas.</p>;
          // Hasta que el usuario elija, se usa la primera edición (la más reciente)
          const idTorneo = idElegido ?? lista[0].id_torneo;
          return (
            <>
              <label className="selector-edicion">
                Edición:{" "}
                <select value={idTorneo} onChange={(e) => setIdElegido(Number(e.target.value))}>
                  {lista.map((ed) => (
                    <option key={ed.id_torneo} value={ed.id_torneo}>{ed.nombre}</option>
                  ))}
                </select>
              </label>
              {/* key: al cambiar la edición se crea una tabla nueva, que vuelve a pedir los datos */}
              <TablaReporte key={idTorneo} pedirDatos={() => pedirDatos(idTorneo)} columnas={columnas} />
            </>
          );
        }}
      </Estado>
    </details>
  );
}