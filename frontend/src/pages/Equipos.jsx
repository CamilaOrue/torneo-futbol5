import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { listarEdiciones } from "../api/ediciones";
import {
  agregarAlPlantel,
  eliminarEquipo,
  jugadoresDisponibles,
  listarEquipos,
  obtenerEquipo,
  quitarDelPlantel,
} from "../api/equipos";
import { listarFacultades } from "../api/facultades";
import { useAuth } from "../auth/useAuth";
import ConfirmarEliminar from "../components/ConfirmarEliminar";
import DataTable from "../components/DataTable";
import EquipoForm from "../components/EquipoForm";
import Estado from "../components/Estado";
import Modal from "../components/Modal";
import { useFetch } from "../hooks/useFetch";
import { ETIQUETA_TIPO } from "../utils";

const MAX_JUGADORES = 10;

/** Primer número de camiseta (1–99) que no usa nadie del plantel. */
function primeraCamisetaLibre(plantel) {
  const usadas = new Set(plantel.map((j) => j.numero_camiseta));
  for (let n = 1; n <= 99; n++) if (!usadas.has(n)) return n;
  return "";
}

/** Formulario en línea para sumar un jugador disponible al plantel. */
function AgregarJugador({ idEquipo, plantel, onAgregado, onCancelar }) {
  const disponibles = useFetch(() => jugadoresDisponibles(idEquipo), [idEquipo]);
  const [ci, setCi] = useState("");
  const [camiseta, setCamiseta] = useState(String(primeraCamisetaLibre(plantel)));
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(ev) {
    ev.preventDefault();
    setErrorGeneral(null);
    const numero = Number(camiseta);
    const errs = {};
    if (!ci) errs.ci_jugador = "Elegí un jugador";
    if (!Number.isInteger(numero) || numero < 1 || numero > 99)
      errs.numero_camiseta = "Debe ser un número entre 1 y 99";
    else if (plantel.some((j) => j.numero_camiseta === numero))
      errs.numero_camiseta = "Ese número ya lo usa otro jugador";
    setErrores(errs);
    if (Object.keys(errs).length) return;

    setEnviando(true);
    try {
      await agregarAlPlantel(idEquipo, { ci_jugador: ci, numero_camiseta: numero });
      const j = disponibles.data.find((d) => d.ci === ci);
      onAgregado(`${j.nombre} ${j.apellido} se sumó al plantel con la camiseta ${numero}.`);
    } catch (e) {
      if (Object.keys(e.fields ?? {}).length) setErrores(e.fields);
      else setErrorGeneral(e.message);
      setEnviando(false);
    }
  }

  const lista = disponibles.data ?? [];

  return (
    <form onSubmit={enviar} noValidate className="formulario agregar-jugador">
      <div className="grilla-form">
        <div className="campo">
          <label htmlFor="agregar-ci">Jugador</label>
          <select
            id="agregar-ci"
            value={ci}
            onChange={(e) => setCi(e.target.value)}
            disabled={disponibles.loading || !lista.length}
            aria-invalid={errores.ci_jugador ? "true" : undefined}
          >
            <option value="">
              {disponibles.loading
                ? "Cargando…"
                : lista.length
                  ? "Seleccionar…"
                  : "No hay jugadores disponibles"}
            </option>
            {lista.map((j) => (
              <option key={j.ci} value={j.ci}>
                {j.apellido}, {j.nombre} · {ETIQUETA_TIPO[j.tipo]} · {j.ci}
              </option>
            ))}
          </select>
          {errores.ci_jugador && (
            <p className="error-campo" role="alert">
              {errores.ci_jugador}
            </p>
          )}
        </div>
        <div className="campo">
          <label htmlFor="agregar-camiseta">N° de camiseta</label>
          <input
            id="agregar-camiseta"
            type="number"
            min={1}
            max={99}
            value={camiseta}
            onChange={(e) => setCamiseta(e.target.value)}
            aria-invalid={errores.numero_camiseta ? "true" : undefined}
          />
          {errores.numero_camiseta && (
            <p className="error-campo" role="alert">
              {errores.numero_camiseta}
            </p>
          )}
        </div>
      </div>
      <p className="sub">
        Solo se listan jugadores de la facultad del equipo que no están en otro equipo de esta
        edición (y docentes/funcionarios si todavía hay cupo).
      </p>
      {(errorGeneral || disponibles.error) && (
        <p className="error" role="alert">
          {errorGeneral || disponibles.error}
        </p>
      )}
      <div className="modal-acciones">
        <button type="button" className="btn" onClick={onCancelar}>
          Cancelar
        </button>
        <button type="submit" className="btn btn-primario" disabled={enviando || !lista.length}>
          {enviando ? "Agregando…" : "Agregar"}
        </button>
      </div>
    </form>
  );
}

function Plantel({ idEquipo, version, onCambio }) {
  const { esAdmin } = useAuth();
  const state = useFetch(() => obtenerEquipo(idEquipo), [idEquipo, version]);
  const [editando, setEditando] = useState(false);
  const [aQuitar, setAQuitar] = useState(null);
  const [agregando, setAgregando] = useState(false);

  async function confirmarQuitar() {
    await quitarDelPlantel(idEquipo, aQuitar.ci);
    setAQuitar(null);
    onCambio(`${aQuitar.nombre} ${aQuitar.apellido} ya no integra el plantel.`);
  }

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
    {
      key: "acciones",
      label: "",
      render: (j) => (
        <button
          className="btn btn-peligro btn-chico"
          aria-label={`Quitar a ${j.nombre} ${j.apellido} del plantel`}
          onClick={() => setAQuitar(j)}
        >
          Quitar
        </button>
      ),
    },
  ].filter((c) => editando || c.key !== "acciones");

  return (
    <Estado {...state}>
      {(e) => {
        const editable = esAdmin && e.estado_torneo === "inscripcion";
        const hayCupo = e.plantel.length < MAX_JUGADORES;
        return (
          <section className="panel">
            <div className="encabezado">
              <div>
                <h3>Plantel de {e.nombre}</h3>
                <p className="sub">
                  {e.facultad} · {e.torneo}
                </p>
              </div>
              {editable && (
                <span className="acciones">
                  {hayCupo && !agregando && (
                    <button className="btn btn-primario" onClick={() => setAgregando(true)}>
                      Agregar jugador
                    </button>
                  )}
                  <button className="btn" onClick={() => setEditando((v) => !v)}>
                    {editando ? "Listo" : "Editar plantel"}
                  </button>
                </span>
              )}
            </div>
            {editable && !hayCupo && (
              <p className="sub">El plantel está completo ({MAX_JUGADORES} jugadores).</p>
            )}
            {editable && hayCupo && agregando && (
              <AgregarJugador
                idEquipo={idEquipo}
                plantel={e.plantel}
                onAgregado={(mensaje) => {
                  setAgregando(false);
                  onCambio(mensaje);
                }}
                onCancelar={() => setAgregando(false)}
              />
            )}
            <DataTable columns={columns} rows={e.plantel} rowKey="ci" vacio="El plantel está vacío." />

            {aQuitar && (
              <ConfirmarEliminar
                titulo="Quitar del plantel"
                onConfirmar={confirmarQuitar}
                onCancelar={() => setAQuitar(null)}
              >
                ¿Quitar a <strong>{aQuitar.nombre} {aQuitar.apellido}</strong> del plantel de{" "}
                {e.nombre}?
                {aQuitar.es_capitan && " Es el capitán: el equipo quedará sin capitán."}
              </ConfirmarEliminar>
            )}
          </section>
        );
      }}
    </Estado>
  );
}

export default function Equipos() {
  const { esAdmin } = useAuth();
  const [params, setParams] = useSearchParams();
  const torneo = params.get("torneo") ?? "";
  const [seleccionado, setSeleccionado] = useState(null);
  const [version, setVersion] = useState(0); // se incrementa para recargar la lista
  const [formulario, setFormulario] = useState(null); // { equipo: null | Equipo }
  const [aEliminar, setAEliminar] = useState(null);
  const [aviso, setAviso] = useState(null);

  const ediciones = useFetch(listarEdiciones);
  const facultades = useFetch(listarFacultades);
  const equipos = useFetch(() => listarEquipos(torneo), [torneo, version]);

  useEffect(() => {
    if (!aviso) return;
    const t = setTimeout(() => setAviso(null), 5000);
    return () => clearTimeout(t);
  }, [aviso]);

  function cambiarTorneo(valor) {
    setSeleccionado(null);
    setParams(valor ? { torneo: valor } : {});
  }

  async function confirmarBaja() {
    await eliminarEquipo(aEliminar.id_equipo);
    if (seleccionado === aEliminar.id_equipo) setSeleccionado(null);
    setAviso(`Equipo eliminado: ${aEliminar.nombre}`);
    setAEliminar(null);
    setVersion((v) => v + 1);
  }

  function guardado(e, accion) {
    setFormulario(null);
    setAviso(`Equipo ${accion}: ${e.nombre}`);
    // Si se filtra por otra edición, se pasa a la del equipo nuevo para que se vea en la lista
    if (torneo && String(e.id_torneo) !== torneo) setParams({ torneo: String(e.id_torneo) });
    setSeleccionado(e.id_equipo);
    setVersion((v) => v + 1);
  }

  const columns = [
    { key: "nombre", label: "Equipo" },
    { key: "facultad", label: "Facultad" },
    { key: "capitan", label: "Capitán", render: (e) => e.capitan ?? "—" },
    { key: "cantidad_jugadores", label: "Jugadores" },
    { key: "torneo", label: "Edición" },
    {
      key: "acciones",
      label: "",
      render: (e) => {
        const enInscripcion = e.estado_torneo === "inscripcion";
        return (
          <span className="acciones">
            <button
              className="link"
              aria-label={`Editar ${e.nombre}`}
              disabled={!enInscripcion}
              title={enInscripcion ? undefined : "Solo se pueden editar equipos de ediciones en inscripción"}
              onClick={(ev) => {
                ev.stopPropagation(); // que no seleccione la fila
                setFormulario({ equipo: e });
              }}
              onKeyDown={(ev) => ev.stopPropagation()}
            >
              Editar
            </button>
            <button
              className="link peligro"
              aria-label={`Eliminar ${e.nombre}`}
              disabled={!enInscripcion}
              title={enInscripcion ? undefined : "Solo se pueden eliminar equipos de ediciones en inscripción"}
              onClick={(ev) => {
                ev.stopPropagation();
                setAEliminar(e);
              }}
              onKeyDown={(ev) => ev.stopPropagation()}
            >
              Eliminar
            </button>
          </span>
        );
      },
    },
  ].filter((c) => esAdmin || c.key !== "acciones");

  return (
    <section>
      <div className="encabezado">
        <h2>Equipos</h2>
        {esAdmin && (
          <button
            className="btn btn-primario"
            onClick={() => setFormulario({ equipo: null })}
            disabled={!ediciones.data || !facultades.data}
          >
            Nuevo equipo
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

      {seleccionado && (
        <Plantel
          key={seleccionado}
          idEquipo={seleccionado}
          version={version}
          onCambio={(mensaje) => {
            setAviso(mensaje);
            setVersion((v) => v + 1); // recarga la lista (cantidad, capitán) y el plantel
          }}
        />
      )}

      {formulario && (
        <Modal
          titulo={formulario.equipo ? "Editar equipo" : "Nuevo equipo"}
          onClose={() => setFormulario(null)}
        >
          <EquipoForm
            equipo={formulario.equipo}
            idTorneo={torneo}
            ediciones={ediciones.data ?? []}
            facultades={facultades.data ?? []}
            onGuardado={guardado}
            onCancelar={() => setFormulario(null)}
          />
        </Modal>
      )}

      {aEliminar && (
        <ConfirmarEliminar
          titulo="Eliminar equipo"
          onConfirmar={confirmarBaja}
          onCancelar={() => setAEliminar(null)}
        >
          ¿Eliminar el equipo <strong>{aEliminar.nombre}</strong> de {aEliminar.torneo}?
          {aEliminar.cantidad_jugadores > 0 &&
            ` También se quitarán los ${aEliminar.cantidad_jugadores} jugadores de su plantel.`}{" "}
          Esta acción no se puede deshacer.
        </ConfirmarEliminar>
      )}
    </section>
  );
}
