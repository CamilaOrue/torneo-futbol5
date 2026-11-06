import { useState } from "react";
import { actualizarEquipo, crearEquipo, obtenerEquipo } from "../api/equipos";
import { useFetch } from "../hooks/useFetch";

const OBLIGATORIO = "Este campo es obligatorio";

function Campo({ campo, label, error, children }) {
  return (
    <div className="campo">
      <label htmlFor={`equipo-${campo}`}>{label}</label>
      {children}
      {error && (
        <p id={`equipo-${campo}-error`} className="error-campo" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

function validar(v) {
  const e = {};
  const nombre = v.nombre.trim();
  if (!nombre) e.nombre = OBLIGATORIO;
  else if (nombre.length > 100) e.nombre = "Máximo 100 caracteres";
  if (!v.id_facultad) e.id_facultad = OBLIGATORIO;
  if (!v.id_torneo) e.id_torneo = OBLIGATORIO;
  return e;
}

/**
 * Alta (equipo = null) o modificación de un equipo.
 * idTorneo: en el alta, edición preseleccionada (la del filtro de la página); se puede cambiar.
 * Al editar, la edición no se modifica y el capitán se elige entre los jugadores del plantel.
 * onGuardado(equipoGuardado, "creado" | "modificado")
 */
export default function EquipoForm({ equipo, idTorneo, ediciones, facultades, onGuardado, onCancelar }) {
  const editar = Boolean(equipo);
  const [valores, setValores] = useState(
    editar
      ? {
          nombre: equipo.nombre,
          id_facultad: String(equipo.id_facultad),
          id_torneo: String(equipo.id_torneo),
          ci_capitan: equipo.ci_capitan ?? "",
        }
      : { nombre: "", id_facultad: "", id_torneo: idTorneo ? String(idTorneo) : "", ci_capitan: "" }
  );
  // El plantel solo hace falta al editar, para elegir el capitán
  const detalle = useFetch(
    () => (editar ? obtenerEquipo(equipo.id_equipo) : Promise.resolve(null)),
    [equipo?.id_equipo]
  );
  const plantel = detalle.data?.plantel ?? [];
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState(null);
  const [enviando, setEnviando] = useState(false);

  const props = (campo) => ({
    id: `equipo-${campo}`,
    value: valores[campo],
    onChange: (e) => setValores((v) => ({ ...v, [campo]: e.target.value })),
    "aria-invalid": errores[campo] ? "true" : undefined,
    "aria-describedby": errores[campo] ? `equipo-${campo}-error` : undefined,
  });

  const edicion = ediciones.find((t) => String(t.id_torneo) === valores.id_torneo);
  const fueraDeInscripcion = !editar && edicion && edicion.estado !== "inscripcion";
  // El backend no deja cambiar la facultad si hay plantel: se avisa y no se permite guardar
  const facultadBloqueada =
    editar && valores.id_facultad !== String(equipo.id_facultad) && plantel.length > 0;

  async function enviar(ev) {
    ev.preventDefault();
    setErrorGeneral(null);

    const errs = validar(valores);
    setErrores(errs);
    if (Object.keys(errs).length) return;

    setEnviando(true);
    try {
      const datos = { nombre: valores.nombre.trim(), id_facultad: Number(valores.id_facultad) };
      const guardado = editar
        ? await actualizarEquipo(equipo.id_equipo, { ...datos, ci_capitan: valores.ci_capitan || null })
        : await crearEquipo({ ...datos, id_torneo: Number(valores.id_torneo) });
      onGuardado(guardado, editar ? "modificado" : "creado");
    } catch (e) {
      if (Object.keys(e.fields ?? {}).length) setErrores(e.fields);
      else if (e.status === 409) setErrores({ nombre: e.message }); // nombre repetido en la edición
      else setErrorGeneral(e.message);
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={enviar} noValidate className="formulario">
      <div className="grilla-form">
        <Campo campo="nombre" label="Nombre" error={errores.nombre}>
          <input {...props("nombre")} maxLength={100} autoComplete="off" required />
        </Campo>
        <Campo campo="id_facultad" label="Facultad" error={errores.id_facultad}>
          <select {...props("id_facultad")} required>
            <option value="">Seleccionar…</option>
            {facultades.map((f) => (
              <option key={f.id_facultad} value={f.id_facultad}>
                {f.nombre}
              </option>
            ))}
          </select>
        </Campo>
        <Campo campo="id_torneo" label="Edición" error={errores.id_torneo}>
          <select {...props("id_torneo")} disabled={editar} required>
            <option value="">Seleccionar…</option>
            {ediciones.map((t) => (
              <option key={t.id_torneo} value={t.id_torneo}>
                {t.nombre}
                {t.estado !== "inscripcion" ? ` (${t.estado})` : ""}
              </option>
            ))}
          </select>
        </Campo>
        {editar && (
          <Campo campo="ci_capitan" label="Capitán" error={errores.ci_capitan}>
            <select {...props("ci_capitan")} disabled={detalle.loading || !plantel.length}>
              {/* El backend no permite quitar el capitán: "Sin capitán" solo si todavía no tiene */}
              {!equipo.ci_capitan && <option value="">Sin capitán</option>}
              {plantel.map((j) => (
                <option key={j.ci} value={j.ci}>
                  {j.apellido}, {j.nombre} (#{j.numero_camiseta})
                </option>
              ))}
            </select>
          </Campo>
        )}
      </div>

      {editar && (
        <p className="sub">
          La edición no se puede cambiar.
          {!detalle.loading && !detalle.error && !plantel.length &&
            " El capitán se elige entre los jugadores del plantel, que está vacío."}
        </p>
      )}
      {detalle.error && (
        <p className="error" role="alert">
          No se pudo cargar el plantel: {detalle.error}
        </p>
      )}
      {facultadBloqueada && (
        <p className="sub">
          No se puede cambiar la facultad de un equipo que ya tiene jugadores en su plantel.
        </p>
      )}
      {fueraDeInscripcion && (
        <p className="sub">
          Esta edición no está en etapa de inscripción: no se le pueden agregar equipos.
        </p>
      )}
      {errorGeneral && (
        <p className="error" role="alert">
          {errorGeneral}
        </p>
      )}

      <div className="modal-acciones">
        <button type="button" className="btn" onClick={onCancelar}>
          Cancelar
        </button>
        <button type="submit" className="btn btn-primario" disabled={enviando || facultadBloqueada}>
          {enviando ? "Guardando…" : "Guardar"}
        </button>
      </div>
    </form>
  );
}
