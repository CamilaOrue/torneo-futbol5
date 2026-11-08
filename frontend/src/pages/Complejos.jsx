import { useEffect, useState } from "react";
import { eliminarCancha, eliminarComplejo, listarCanchasDe, listarComplejos } from "../api/complejos";
import { useAuth } from "../auth/useAuth";
import CanchaForm from "../components/CanchaForm";
import ComplejoForm from "../components/ComplejoForm";
import ConfirmarEliminar from "../components/ConfirmarEliminar";
import DataTable from "../components/DataTable";
import Estado from "../components/Estado";
import Modal from "../components/Modal";
import { useDebounce } from "../hooks/useDebounce";
import { useFetch } from "../hooks/useFetch";
import { ETIQUETA_SUPERFICIE } from "../utils";

function Canchas({ complejo, version, onCambio }) {
  const { esAdmin } = useAuth();
  const state = useFetch(() => listarCanchasDe(complejo.id_complejo), [complejo.id_complejo, version]);
  const [formulario, setFormulario] = useState(null); // { cancha: null | Cancha }
  const [aEliminar, setAEliminar] = useState(null);

  function guardada(c, accion) {
    setFormulario(null);
    onCambio(`Cancha ${accion}: ${c.nombre_cancha}`);
  }

  async function confirmarBaja() {
    await eliminarCancha(complejo.id_complejo, aEliminar.nombre_cancha);
    setAEliminar(null);
    onCambio(`Cancha eliminada: ${aEliminar.nombre_cancha}`);
  }

  const columns = [
    { key: "nombre_cancha", label: "Cancha" },
    {
      key: "superficie",
      label: "Superficie",
      render: (c) => ETIQUETA_SUPERFICIE[c.superficie] ?? c.superficie,
    },
    { key: "techada", label: "Techada", render: (c) => (c.techada ? "Sí" : "No") },
    {
      key: "acciones",
      label: "",
      render: (c) => (
        <span className="acciones">
          <button
            className="link"
            aria-label={`Editar la cancha ${c.nombre_cancha}`}
            onClick={() => setFormulario({ cancha: c })}
          >
            Editar
          </button>
          <button
            className="link peligro"
            aria-label={`Eliminar la cancha ${c.nombre_cancha}`}
            onClick={() => setAEliminar(c)}
          >
            Eliminar
          </button>
        </span>
      ),
    },
  ].filter((c) => esAdmin || c.key !== "acciones");

  return (
    <section className="panel">
      <div className="encabezado">
        <div>
          <h3>Canchas de {complejo.nombre}</h3>
          <p className="sub">
            {complejo.direccion} · {complejo.departamento}
          </p>
        </div>
        {esAdmin && (
          <button className="btn btn-primario" onClick={() => setFormulario({ cancha: null })}>
            Nueva cancha
          </button>
        )}
      </div>

      <Estado {...state}>
        {(lista) => (
          <DataTable
            columns={columns}
            rows={lista}
            rowKey="nombre_cancha"
            vacio="Este complejo todavía no tiene canchas."
          />
        )}
      </Estado>

      {formulario && (
        <Modal
          titulo={formulario.cancha ? "Editar cancha" : "Nueva cancha"}
          onClose={() => setFormulario(null)}
        >
          <CanchaForm
            idComplejo={complejo.id_complejo}
            cancha={formulario.cancha}
            onGuardado={guardada}
            onCancelar={() => setFormulario(null)}
          />
        </Modal>
      )}

      {aEliminar && (
        <ConfirmarEliminar
          titulo="Eliminar cancha"
          onConfirmar={confirmarBaja}
          onCancelar={() => setAEliminar(null)}
        >
          ¿Eliminar la cancha <strong>{aEliminar.nombre_cancha}</strong> de {complejo.nombre}? No se
          puede eliminar si tiene partidos asignados. Esta acción no se puede deshacer.
        </ConfirmarEliminar>
      )}
    </section>
  );
}

export default function Complejos() {
  const { esAdmin } = useAuth();
  const [texto, setTexto] = useState("");
  const q = useDebounce(texto.trim(), 300);
  const [seleccionado, setSeleccionado] = useState(null);
  const [version, setVersion] = useState(0); // se incrementa para recargar la lista
  const [formulario, setFormulario] = useState(null); // { complejo: null | Complejo }
  const [aEliminar, setAEliminar] = useState(null);
  const [aviso, setAviso] = useState(null);

  const complejos = useFetch(() => listarComplejos({ q }), [q, version]);
  const complejoSeleccionado = complejos.data?.find((c) => c.id_complejo === seleccionado);

  useEffect(() => {
    if (!aviso) return;
    const t = setTimeout(() => setAviso(null), 5000);
    return () => clearTimeout(t);
  }, [aviso]);

  async function confirmarBaja() {
    await eliminarComplejo(aEliminar.id_complejo);
    if (seleccionado === aEliminar.id_complejo) setSeleccionado(null);
    setAviso(`Complejo eliminado: ${aEliminar.nombre}`);
    setAEliminar(null);
    setVersion((v) => v + 1);
  }

  function guardado(c, accion) {
    setFormulario(null);
    setAviso(`Complejo ${accion}: ${c.nombre}`);
    setSeleccionado(c.id_complejo);
    setVersion((v) => v + 1);
  }

  const columns = [
    { key: "nombre", label: "Complejo" },
    { key: "direccion", label: "Dirección" },
    { key: "departamento", label: "Departamento" },
    {
      key: "acciones",
      label: "",
      render: (c) => (
        <span className="acciones">
          <button
            className="link"
            aria-label={`Editar ${c.nombre}`}
            onClick={(ev) => {
              ev.stopPropagation(); // que no seleccione la fila
              setFormulario({ complejo: c });
            }}
            onKeyDown={(ev) => ev.stopPropagation()}
          >
            Editar
          </button>
          <button
            className="link peligro"
            aria-label={`Eliminar ${c.nombre}`}
            onClick={(ev) => {
              ev.stopPropagation();
              setAEliminar(c);
            }}
            onKeyDown={(ev) => ev.stopPropagation()}
          >
            Eliminar
          </button>
        </span>
      ),
    },
  ].filter((c) => esAdmin || c.key !== "acciones");

  return (
    <section>
      <div className="encabezado">
        <h2>Complejos</h2>
        {esAdmin && (
          <button className="btn btn-primario" onClick={() => setFormulario({ complejo: null })}>
            Nuevo complejo
          </button>
        )}
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
            placeholder="Nombre o departamento"
            onChange={(e) => setTexto(e.target.value)}
          />
        </label>
      </div>

      <Estado {...complejos}>
        {(lista) => (
          <>
            <DataTable
              columns={columns}
              rows={lista}
              rowKey="id_complejo"
              selectedKey={seleccionado}
              onRowClick={(c) => setSeleccionado(c.id_complejo)}
              vacio="Ningún complejo coincide con la búsqueda."
            />
            {lista.length > 0 && !seleccionado && (
              <p className="sub">Hacé clic en un complejo para ver sus canchas.</p>
            )}
          </>
        )}
      </Estado>

      {complejoSeleccionado && (
        <Canchas
          key={complejoSeleccionado.id_complejo}
          complejo={complejoSeleccionado}
          version={version}
          onCambio={(mensaje) => {
            setAviso(mensaje);
            setVersion((v) => v + 1); // recarga la lista y las canchas
          }}
        />
      )}

      {formulario && (
        <Modal
          titulo={formulario.complejo ? "Editar complejo" : "Nuevo complejo"}
          onClose={() => setFormulario(null)}
        >
          <ComplejoForm
            complejo={formulario.complejo}
            onGuardado={guardado}
            onCancelar={() => setFormulario(null)}
          />
        </Modal>
      )}

      {aEliminar && (
        <ConfirmarEliminar
          titulo="Eliminar complejo"
          onConfirmar={confirmarBaja}
          onCancelar={() => setAEliminar(null)}
        >
          ¿Eliminar el complejo <strong>{aEliminar.nombre}</strong>? No se puede eliminar si todavía
          tiene canchas. Esta acción no se puede deshacer.
        </ConfirmarEliminar>
      )}
    </section>
  );
}
