import { useEffect, useState } from "react";
import { listarFacultades } from "../api/facultades";
import { eliminarJugador, listarJugadores } from "../api/jugadores";
import ConfirmarEliminar from "../components/ConfirmarEliminar";
import DataTable from "../components/DataTable";
import Estado from "../components/Estado";
import JugadorForm from "../components/JugadorForm";
import Modal from "../components/Modal";
import { useDebounce } from "../hooks/useDebounce";
import { useFetch } from "../hooks/useFetch";
import { ETIQUETA_TIPO, formatFecha } from "../utils";

export default function Jugadores() {
  const [texto, setTexto] = useState("");
  const [idFacultad, setIdFacultad] = useState("");
  const [tipo, setTipo] = useState("");
  const q = useDebounce(texto.trim(), 300);

  const [version, setVersion] = useState(0); // se incrementa para recargar la lista
  const [formulario, setFormulario] = useState(null); // { jugador: null | Jugador }
  const [aEliminar, setAEliminar] = useState(null);
  const [aviso, setAviso] = useState(null);

  const facultades = useFetch(listarFacultades);
  const jugadores = useFetch(
    () => listarJugadores({ q, idFacultad, tipo }),
    [q, idFacultad, tipo, version]
  );

  useEffect(() => {
    if (!aviso) return;
    const t = setTimeout(() => setAviso(null), 5000);
    return () => clearTimeout(t);
  }, [aviso]);

  function guardado(j, accion) {
    setFormulario(null);
    setAviso(`Jugador ${accion}: ${j.nombre} ${j.apellido}`);
    setVersion((v) => v + 1);
  }

  async function confirmarBaja() {
    await eliminarJugador(aEliminar.ci);
    setAviso(`Jugador eliminado: ${aEliminar.nombre} ${aEliminar.apellido}`);
    setAEliminar(null);
    setVersion((v) => v + 1);
  }

  const columns = [
    { key: "ci", label: "CI" },
    { key: "jugador", label: "Jugador", render: (j) => `${j.apellido}, ${j.nombre}` },
    { key: "email", label: "Email" },
    { key: "facultad", label: "Facultad" },
    { key: "tipo", label: "Tipo", render: (j) => ETIQUETA_TIPO[j.tipo] },
    { key: "equipo_actual", label: "Equipo", render: (j) => j.equipo_actual ?? "—" },
    {
      key: "fecha_nacimiento",
      label: "Nacimiento",
      render: (j) => formatFecha(j.fecha_nacimiento),
    },
    {
      key: "acciones",
      label: "",
      render: (j) => (
        <span className="acciones">
          <button
            className="link"
            aria-label={`Editar a ${j.nombre} ${j.apellido}`}
            onClick={() => setFormulario({ jugador: j })}
          >
            Editar
          </button>
          <button
            className="link peligro"
            aria-label={`Eliminar a ${j.nombre} ${j.apellido}`}
            onClick={() => setAEliminar(j)}
          >
            Eliminar
          </button>
        </span>
      ),
    },
  ];

  return (
    <section>
      <div className="encabezado">
        <h2>Jugadores</h2>
        <button
          className="btn btn-primario"
          onClick={() => setFormulario({ jugador: null })}
          disabled={!facultades.data}
        >
          Nuevo jugador
        </button>
      </div>

      {aviso && (
        <p className="aviso" role="status">
          {aviso}
        </p>
      )}

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

      {formulario && (
        <Modal
          titulo={formulario.jugador ? "Editar jugador" : "Nuevo jugador"}
          onClose={() => setFormulario(null)}
        >
          <JugadorForm
            jugador={formulario.jugador}
            facultades={facultades.data ?? []}
            onGuardado={guardado}
            onCancelar={() => setFormulario(null)}
          />
        </Modal>
      )}

      {aEliminar && (
        <ConfirmarEliminar
          titulo="Eliminar jugador"
          onConfirmar={confirmarBaja}
          onCancelar={() => setAEliminar(null)}
        >
          ¿Eliminar a{" "}
          <strong>
            {aEliminar.nombre} {aEliminar.apellido}
          </strong>{" "}
          (CI {aEliminar.ci})? Esta acción no se puede deshacer.
        </ConfirmarEliminar>
      )}
    </section>
  );
}
