/** "2026-09-28" -> "28/09/2026" (sin pasar por Date para evitar corrimientos de zona horaria). */
export function formatFecha(iso) {
  if (!iso) return "—";
  const [y, m, d] = iso.split("-");
  return `${d}/${m}/${y}`;
}

export const ETIQUETA_ESTADO = {
  inscripcion: "Inscripción",
  "en curso": "En curso",
  finalizado: "Finalizado",
};

export const ETIQUETA_TIPO = {
  grado: "Grado",
  posgrado: "Posgrado",
  docente: "Docente",
  funcionario: "Funcionario",
};
