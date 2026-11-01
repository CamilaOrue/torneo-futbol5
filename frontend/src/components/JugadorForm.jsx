import { useState } from "react";
import { actualizarJugador, crearJugador } from "../api/jugadores";
import { ETIQUETA_TIPO } from "../utils";
import { ayerISO, normalizarCi, validarJugador } from "../validaciones";

const VACIO = {
  ci: "",
  nombre: "",
  apellido: "",
  email: "",
  fecha_nacimiento: "",
  id_facultad: "",
  tipo: "",
};

function Campo({ campo, label, error, children }) {
  return (
    <div className="campo">
      <label htmlFor={`jugador-${campo}`}>{label}</label>
      {children}
      {error && (
        <p id={`jugador-${campo}-error`} className="error-campo" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

/**
 * Alta (jugador = null) o modificación de un jugador.
 * onGuardado(jugadorGuardado, "creado" | "modificado")
 */
export default function JugadorForm({ jugador, facultades, onGuardado, onCancelar }) {
  const editar = Boolean(jugador);
  const [valores, setValores] = useState(
    editar ? { ...jugador, id_facultad: String(jugador.id_facultad) } : VACIO
  );
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState(null);
  const [enviando, setEnviando] = useState(false);

  const props = (campo) => ({
    id: `jugador-${campo}`,
    value: valores[campo],
    onChange: (e) => setValores((v) => ({ ...v, [campo]: e.target.value })),
    "aria-invalid": errores[campo] ? "true" : undefined,
    "aria-describedby": errores[campo] ? `jugador-${campo}-error` : undefined,
  });

  async function enviar(ev) {
    ev.preventDefault();
    setErrorGeneral(null);

    const errs = validarJugador(valores, { modo: editar ? "editar" : "crear" });
    setErrores(errs);
    if (Object.keys(errs).length) return;

    const datos = {
      nombre: valores.nombre.trim(),
      apellido: valores.apellido.trim(),
      email: valores.email.trim(),
      fecha_nacimiento: valores.fecha_nacimiento,
      id_facultad: Number(valores.id_facultad),
      tipo: valores.tipo,
    };

    setEnviando(true);
    try {
      const guardado = editar
        ? await actualizarJugador(jugador.ci, datos)
        : await crearJugador({ ci: normalizarCi(valores.ci), ...datos });
      onGuardado(guardado, editar ? "modificado" : "creado");
    } catch (e) {
      // Errores de la API: por campo si se puede, si no como mensaje general
      if (Object.keys(e.fields ?? {}).length) setErrores(e.fields);
      else setErrorGeneral(e.message);
      setEnviando(false);
    }
  }

  return (
    <form onSubmit={enviar} noValidate className="formulario">
      <div className="grilla-form">
        <Campo campo="ci" label="CI" error={errores.ci}>
          <input
            {...props("ci")}
            inputMode="numeric"
            maxLength={12}
            autoComplete="off"
            disabled={editar}
            placeholder="1.234.567-8"
            required
          />
        </Campo>
        <Campo campo="email" label="Email" error={errores.email}>
          <input {...props("email")} type="email" maxLength={100} autoComplete="off" required />
        </Campo>
        <Campo campo="nombre" label="Nombre" error={errores.nombre}>
          <input {...props("nombre")} maxLength={50} autoComplete="off" required />
        </Campo>
        <Campo campo="apellido" label="Apellido" error={errores.apellido}>
          <input {...props("apellido")} maxLength={50} autoComplete="off" required />
        </Campo>
        <Campo campo="fecha_nacimiento" label="Fecha de nacimiento" error={errores.fecha_nacimiento}>
          <input
            {...props("fecha_nacimiento")}
            type="date"
            min="1900-01-01"
            max={ayerISO()}
            required
          />
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
        <Campo campo="tipo" label="Tipo" error={errores.tipo}>
          <select {...props("tipo")} required>
            <option value="">Seleccionar…</option>
            {Object.entries(ETIQUETA_TIPO).map(([valor, etiqueta]) => (
              <option key={valor} value={valor}>
                {etiqueta}
              </option>
            ))}
          </select>
        </Campo>
      </div>

      {editar && (
        <p className="sub">La CI es la clave del jugador y no se puede modificar.</p>
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
