import { useState } from "react";
import { listarFacultades } from "../api/facultades";
import { listarJugadores } from "../api/jugadores";
import DataTable from "../components/DataTable";
import Estado from "../components/Estado";
import { useDebounce } from "../hooks/useDebounce";
import { useFetch } from "../hooks/useFetch";
import { ETIQUETA_TIPO, formatFecha } from "../utils";

const columns = [
  { key: "ci", label: "CI" },
  { key: "jugador", label: "Jugador", render: (j) => `${j.apellido}, ${j.nombre}` },
  { key: "email", label: "Email" },
  { key: "facultad", label: "Facultad" },
  { key: "tipo", label: "Tipo", render: (j) => ETIQUETA_TIPO[j.tipo] },
  { key: "equipo_actual", label: "Equipo", render: (j) => j.equipo_actual ?? "—" },
  { key: "fecha_nacimiento", label: "Nacimiento", render: (j) => formatFecha(j.fecha_nacimiento) },
];

export default function Jugadores() {
  const [texto, setTexto] = useState("");
  const [idFacultad, setIdFacultad] = useState("");
  const [tipo, setTipo] = useState("");
  const q = useDebounce(texto.trim(), 300);

  const facultades = useFetch(listarFacultades);
  const jugadores = useFetch(
    () => listarJugadores({ q, idFacultad, tipo }),
    [q, idFacultad, tipo]
  );

  return (
    <section>
      <h2>Jugadores</h2>

      <div className="filtros">
        <label>
          Buscar
          <input
            type="search"
            value={texto}
            maxLength={100}
            placeholder="Nombre, apellido, CI o email"
            onChange={(e) => setTexto(e.target.value)}
          />
        </label>
        <label>
          Facultad
          <select value={idFacultad} onChange={(e) => setIdFacultad(e.target.value)}>
            <option value="">Todas</option>
            {(facultades.data ?? []).map((f) => (
              <option key={f.id_facultad} value={f.id_facultad}>
                {f.nombre}
              </option>
            ))}
          </select>
        </label>
        <label>
          Tipo
          <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
            <option value="">Todos</option>
            {Object.entries(ETIQUETA_TIPO).map(([valor, etiqueta]) => (
              <option key={valor} value={valor}>
                {etiqueta}
              </option>
            ))}
          </select>
        </label>
      </div>

      <Estado {...jugadores}>
        {(lista) => (
          <>
            <p className="sub">
              {lista.length} {lista.length === 1 ? "jugador" : "jugadores"}
            </p>
            <DataTable
              columns={columns}
              rows={lista}
              rowKey="ci"
              vacio="Ningún jugador coincide con los filtros."
            />
          </>
        )}
      </Estado>
    </section>
  );
}
