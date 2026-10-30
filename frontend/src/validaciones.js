/** Validaciones del formulario de jugadores (espejo de las del backend). */

const NOMBRE_RE = /^(?=.*\p{L})[\p{L} '.-]+$/u;
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const CI_RE = /^[0-9]{7,8}$/;
const OBLIGATORIO = "Este campo es obligatorio";

/** "1.234.567-8" -> "12345678" */
export const normalizarCi = (ci) => ci.replace(/[.\-\s]/g, "");

const pad = (n) => String(n).padStart(2, "0");

/** Último día válido para una fecha de nacimiento (debe ser anterior a hoy), en formato AAAA-MM-DD. */
export function ayerISO() {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

/** Devuelve { campo: mensaje } con los errores; vacío si todo está bien. */
export function validarJugador(v, { modo }) {
  const e = {};

  if (modo === "crear") {
    const ci = normalizarCi(v.ci);
    if (!ci) e.ci = OBLIGATORIO;
    else if (!CI_RE.test(ci)) e.ci = "La CI debe tener 7 u 8 dígitos (se aceptan puntos y guión)";
  }

  for (const campo of ["nombre", "apellido"]) {
    const t = v[campo].trim().replace(/\s+/g, " ");
    if (!t) e[campo] = OBLIGATORIO;
    else if (t.length > 50) e[campo] = "Máximo 50 caracteres";
    else if (!NOMBRE_RE.test(t))
      e[campo] = "Solo puede contener letras, espacios, apóstrofes, puntos y guiones";
  }

  const email = v.email.trim();
  if (!email) e.email = OBLIGATORIO;
  else if (email.length > 100) e.email = "Máximo 100 caracteres";
  else if (!EMAIL_RE.test(email)) e.email = "El email no tiene un formato válido";

  if (!v.fecha_nacimiento) e.fecha_nacimiento = OBLIGATORIO;
  else if (v.fecha_nacimiento > ayerISO())
    e.fecha_nacimiento = "La fecha de nacimiento debe ser anterior a hoy";
  else if (v.fecha_nacimiento < "1900-01-01") e.fecha_nacimiento = "La fecha de nacimiento no es válida";

  if (!v.id_facultad) e.id_facultad = "Seleccioná una facultad";
  if (!v.tipo) e.tipo = "Seleccioná un tipo";

  return e;
}
