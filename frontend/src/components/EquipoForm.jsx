import { useState } from "react";
import { crearEquipo } from "../api/equipos";

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
 * Alta de un equipo.
 * idTorneo: edición preseleccionada (la del filtro de la página), se puede cambiar.
 * onGuardado(equipoCreado)
 */
export default function EquipoForm({ idTorneo, ediciones, facultades, onGuardado, onCancelar }) {
  const [valores, setValores] = useState({
    nombre: "",
    id_facultad: "",
    id_torneo: idTorneo ? String(idTorneo) : "",
  });
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
  const fueraDeInscripcion = edicion && edicion.estado !== "inscripcion";

  async function enviar(ev) {
    ev.preventDefault();
    setErrorGeneral(null);

    const errs = validar(valores);
    setErrores(errs);
    if (Object.keys(errs).length) return;

    setEnviando(true);
    try {
      const creado = await crearEquipo({
        nombre: valores.nombre.trim(),
        id_facultad: Number(valores.id_facultad),
        id_torneo: Number(valores.id_torneo),
      });
      onGuardado(creado);
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
          <select {...props("id_torneo")} required>
            <option value="">Seleccionar…</option>
            {ediciones.map((t) => (
              <option key={t.id_torneo} value={t.id_torneo}>
                {t.nombre}
                {t.estado !== "inscripcion" ? ` (${t.estado})` : ""}
              </option>
            ))}
          </select>
        </Campo>
      </div>

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
        <button type="submit" className="btn btn-primario" disabled={enviando}>
          {enviando ? "Guardando…" : "Guardar"}
        </button>
      </div>
    </form>
  );
}
