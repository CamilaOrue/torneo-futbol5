import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { listarEdiciones } from "../api/ediciones";
import { listarEquipos, obtenerEquipo } from "../api/equipos";
import DataTable from "../components/DataTable";
import Estado from "../components/Estado";
import { useFetch } from "../hooks/useFetch";
import { ETIQUETA_TIPO } from "../utils";

function Plantel({ idEquipo }) {
  const state = useFetch(() => obtenerEquipo(idEquipo), [idEquipo]);

  const columns = [
    {
      key: "numero_camiseta",
      label: "N°",
      render: (j) => <span className="camiseta">{j.numero_camiseta}</span>,
    },
    {
      key: "jugador",
      label: "Jugador",
      render: (j) => (
        <>
          {j.apellido}, {j.nombre}
          {j.es_capitan && (
            <span className="badge badge-capitan" title="Capitán">
              C
            </span>
          )}
        </>
      ),
    },
    { key: "tipo", label: "Tipo", render: (j) => ETIQUETA_TIPO[j.tipo] },
    { key: "ci", label: "CI" },
  ];

  return (
    <Estado {...state}>
      {(e) => (
        <section className="panel">
          <h3>Plantel de {e.nombre}</h3>
          <p className="sub">
            {e.facultad} · {e.torneo}
          </p>
          <DataTable columns={columns} rows={e.plantel} rowKey="ci" vacio="El plantel está vacío." />
        </section>
      )}
    </Estado>
  );
}

export default function Equipos() {
  const [params, setParams] = useSearchParams();
  const torneo = params.get("torneo") ?? "";
  const [seleccionado, setSeleccionado] = useState(null);

  const ediciones = useFetch(listarEdiciones);
  const equipos = useFetch(() => listarEquipos(torneo), [torneo]);

  function cambiarTorneo(valor) {
    setSeleccionado(null);
    setParams(valor ? { torneo: valor } : {});
  }

  const columns = [
    { key: "nombre", label: "Equipo" },
    { key: "facultad", label: "Facultad" },
    { key: "capitan", label: "Capitán", render: (e) => e.capitan ?? "—" },
    { key: "cantidad_jugadores", label: "Jugadores" },
    { key: "torneo", label: "Edición" },
  ];

  return (
    <section>
      <h2>Equipos</h2>

      <div className="filtros">
        <label>
          Edición
          <select value={torneo} onChange={(e) => cambiarTorneo(e.target.value)}>
            <option value="">Todas</option>
            {(ediciones.data ?? []).map((t) => (
              <option key={t.id_torneo} value={t.id_torneo}>
                {t.nombre}
              </option>
            ))}
          </select>
        </label>
      </div>

      <Estado {...equipos}>
        {(lista) => (
          <>
            <DataTable
              columns={columns}
              rows={lista}
              rowKey="id_equipo"
              selectedKey={seleccionado}
              onRowClick={(e) => setSeleccionado(e.id_equipo)}
              vacio="No hay equipos para la edición seleccionada."
            />
            {lista.length > 0 && !seleccionado && (
              <p className="sub">Hacé clic en un equipo para ver su plantel.</p>
            )}
          </>
        )}
      </Estado>

      {seleccionado && <Plantel key={seleccionado} idEquipo={seleccionado} />}
    </section>
  );
}
