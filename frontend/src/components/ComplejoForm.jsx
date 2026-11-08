import { useState } from "react";
import { actualizarComplejo, crearComplejo } from "../api/complejos";
import { DEPARTAMENTOS } from "../utils";

const OBLIGATORIO = "Este campo es obligatorio";

function Campo({ campo, label, error, children }) {
  return (
    <div className="campo">
      <label htmlFor={`complejo-${campo}`}>{label}</label>
      {children}
      {error && (
        <p id={`complejo-${campo}-error`} className="error-campo" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

function validar(v) {
  const e = {};
  const largos = { nombre: 100, direccion: 150, departamento: 50 };
  for (const [campo, max] of Object.entries(largos)) {
    const texto = v[campo].trim();
    if (!texto) e[campo] = OBLIGATORIO;
    else if (texto.length > max) e[campo] = `Máximo ${max} caracteres`;
  }
  return e;
}

/**
 * Alta (complejo = null) o modificación de un complejo deportivo.
 * onGuardado(complejoGuardado, "creado" | "modificado")
 */
export default function ComplejoForm({ complejo, onGuardado, onCancelar }) {
  const editar = Boolean(complejo);
  const [valores, setValores] = useState(
    editar
      ? { nombre: complejo.nombre, direccion: complejo.direccion, departamento: complejo.departamento }
      : { nombre: "", direccion: "", departamento: "" }
  );
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState(null);
  const [enviando, setEnviando] = useState(false);

  const props = (campo) => ({
    id: `complejo-${campo}`,
    value: valores[campo],
    onChange: (e) => setValores((v) => ({ ...v, [campo]: e.target.value })),
    "aria-invalid": errores[campo] ? "true" : undefined,
    "aria-describedby": errores[campo] ? `complejo-${campo}-error` : undefined,
  });

  // Si el complejo tiene un departamento que no está en la lista, se agrega como opción
  const departamentos =
    !valores.departamento || DEPARTAMENTOS.includes(valores.departamento)
      ? DEPARTAMENTOS
      : [valores.departamento, ...DEPARTAMENTOS];

  async function enviar(ev) {
    ev.preventDefault();
    setErrorGeneral(null);

    const errs = validar(valores);
    setErrores(errs);
    if (Object.keys(errs).length) return;

    setEnviando(true);
    try {
      const datos = {
        nombre: valores.nombre.trim(),
        direccion: valores.direccion.trim(),
        departamento: valores.departamento.trim(),
      };
      const guardado = editar
        ? await actualizarComplejo(complejo.id_complejo, datos)
        : await crearComplejo(datos);
      onGuardado(guardado, editar ? "modificado" : "creado");
    } catch (e) {
      if (Object.keys(e.fields ?? {}).length) setErrores(e.fields);
      else if (e.status === 409) setErrores({ nombre: e.message }); // nombre repetido
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
        <Campo campo="departamento" label="Departamento" error={errores.departamento}>
          <select {...props("departamento")} required>
            <option value="">Seleccionar…</option>
            {departamentos.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </Campo>
        <Campo campo="direccion" label="Dirección" error={errores.direccion}>
          <input {...props("direccion")} maxLength={150} autoComplete="off" required />
        </Campo>
      </div>

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
