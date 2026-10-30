import { useNavigate } from "react-router-dom";
import { listarEdiciones } from "../api/ediciones";
import DataTable from "../components/DataTable";
import Estado from "../components/Estado";
import { useFetch } from "../hooks/useFetch";
import { ETIQUETA_ESTADO, formatFecha } from "../utils";

export default function Ediciones() {
  const navigate = useNavigate();
  const state = useFetch(listarEdiciones);

  const columns = [
    { key: "nombre", label: "Edición" },
    { key: "periodo", label: "Semestre", render: (t) => `${t.anio} · S${t.semestre}` },
    {
      key: "fechas",
      label: "Fechas",
      render: (t) => `${formatFecha(t.fecha_inicio)} – ${formatFecha(t.fecha_fin)}`,
    },
    {
      key: "estado",
      label: "Estado",
      render: (t) => (
        <span className={`badge badge-${t.estado.replace(" ", "-")}`}>
          {ETIQUETA_ESTADO[t.estado]}
        </span>
      ),
    },
    { key: "cantidad_equipos", label: "Equipos" },
    {
      key: "partidos",
      label: "Partidos jugados",
      render: (t) => `${t.partidos_jugados} / ${t.cantidad_partidos}`,
    },
    {
      key: "acciones",
      label: "",
      render: (t) => (
        <button
          className="link"
          onClick={() => navigate(`/equipos?torneo=${t.id_torneo}`)}
        >
          Ver equipos
        </button>
      ),
    },
  ];

  return (
    <section>
      <h2>Ediciones</h2>
      <Estado {...state}>
        {(ediciones) => (
          <DataTable
            columns={columns}
            rows={ediciones}
            rowKey="id_torneo"
            vacio="Todavía no hay ediciones cargadas."
          />
        )}
      </Estado>
    </section>
  );
}
