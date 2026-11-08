import { useState } from "react";
import { actualizarCancha, crearCancha } from "../api/complejos";
import { ETIQUETA_SUPERFICIE } from "../utils";

const OBLIGATORIO = "Este campo es obligatorio";

function Campo({ campo, label, error, children }) {
  return (
    <div className="campo">
      <label htmlFor={`cancha-${campo}`}>{label}</label>
      {children}
      {error && (
        <p id={`cancha-${campo}-error`} className="error-campo" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

function validar(v) {
  const e = {};
  const nombre = v.nombre_cancha.trim();
  if (!nombre) e.nombre_cancha = OBLIGATORIO;
  else if (nombre.length > 50) e.nombre_cancha = "Máximo 50 caracteres";
  if (!v.superficie) e.superficie = OBLIGATORIO;
  return e;
}

/**
 * Alta (cancha = null) o modificación de una cancha del complejo `idComplejo`.
 * Al editar, el nombre no se modifica: junto con el complejo es la clave de la cancha.
 * onGuardado(canchaGuardada, "creada" | "modificada")
 */
export default function CanchaForm({ idComplejo, cancha, onGuardado, onCancelar }) {
  const editar = Boolean(cancha);
  const [valores, setValores] = useState(
    editar
      ? {
          nombre_cancha: cancha.nombre_cancha,
          superficie: cancha.superficie,
          techada: String(Boolean(cancha.techada)),
        }
      : { nombre_cancha: "", superficie: "", techada: "false" }
  );
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState(null);
  const [enviando, setEnviando] = useState(false);

  const props = (campo) => ({
    id: `cancha-${campo}`,
    value: valores[campo],
    onChange: (e) => setValores((v) => ({ ...v, [campo]: e.target.value })),
    "aria-invalid": errores[campo] ? "true" : undefined,
    "aria-describedby": errores[campo] ? `cancha-${campo}-error` : undefined,
  });

  async function enviar(ev) {
    ev.preventDefault();
    setErrorGeneral(null);

    const errs = validar(valores);
    setErrores(errs);
    if (Object.keys(errs).length) return;

    setEnviando(true);
    try {
      const datos = {
        nombre_cancha: valores.nombre_cancha.trim(),
        superficie: valores.superficie,
        techada: valores.techada === "true",
      };
      const guardada = editar
        ? await actualizarCancha(idComplejo, cancha.nombre_cancha, datos)
        : await crearCancha(idComplejo, datos);
      onGuardado(guardada, editar ? "modificada" : "creada");
    } catch (e) {
      if (Object.keys(e.fields ?? {}).length) setErrores(e.fields);
      else if (e.status === 409) setErrores({ nombre_cancha: e.message }); // nombre repetido en el complejo
      else setErrorGeneral(e.message);
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={enviar} noValidate className="formulario">
      <div className="grilla-form">
        <Campo campo="nombre_cancha" label="Nombre" error={errores.nombre_cancha}>
          <input
            {...props("nombre_cancha")}
            maxLength={50}
            autoComplete="off"
            disabled={editar}
            required
          />
        </Campo>
        <Campo campo="superficie" label="Superficie" error={errores.superficie}>
          <select {...props("superficie")} required>
            <option value="">Seleccionar…</option>
            {Object.entries(ETIQUETA_SUPERFICIE).map(([valor, etiqueta]) => (
              <option key={valor} value={valor}>
                {etiqueta}
              </option>
            ))}
          </select>
        </Campo>
        <Campo campo="techada" label="Techada" error={errores.techada}>
          <select {...props("techada")}>
            <option value="false">No</option>
            <option value="true">Sí</option>
          </select>
        </Campo>
      </div>

      {editar && <p className="sub">El nombre de la cancha no se puede cambiar.</p>}
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
