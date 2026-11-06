import DataTable from "./DataTable";
import Estado from "./Estado";
import { useFetch } from "../hooks/useFetch";

export function TablaReporte({ pedirDatos, columnas }) {
  const state = useFetch(pedirDatos);

  return (
    <Estado {...state}>
      {(datos) => {
        // Algunos reportes devuelven una sola fila (un objeto) en lugar de una lista
        const lista = Array.isArray(datos) ? datos : [datos];
        // Los reportes no tienen un campo único: se numera cada fila para usarlo como clave
        const filas = lista.map((fila, i) => ({ ...fila, _fila: i }));
        return (
          <DataTable columns={columnas} rows={filas} rowKey="_fila" vacio="No hay datos para este reporte." />
        );
      }}
    </Estado>
  );
}

export default function ReporteTabla({ titulo, pedirDatos, columnas, abierto = false }) {
  return (
    <details className="reporte" open={abierto}>
      <summary>{titulo}</summary>
      <TablaReporte pedirDatos={pedirDatos} columnas={columnas} />
    </details>
  );
}