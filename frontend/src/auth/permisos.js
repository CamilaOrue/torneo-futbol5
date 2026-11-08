/**
 * Qué secciones ve cada tipo de usuario (según la letra del obligatorio):
 * - Visitante sin sesión: solo los reportes.
 * - Planillero: registra planillas, goles y tarjetas, y ve los reportes.
 * - Administrador: gestiona toda la información del torneo.
 */
export const ANONIMO = "anonimo";

export const SECCIONES = [
  { to: "/ediciones", label: "Ediciones", roles: ["administrador"] },
  { to: "/equipos", label: "Equipos", roles: ["administrador"] },
  { to: "/jugadores", label: "Jugadores", roles: ["administrador"] },
  { to: "/reportes", label: "Reportes", roles: ["administrador", "planillero", ANONIMO] },
  { to: "/planilla", label: "Planilla", roles: ["administrador", "planillero"] },
  { to: "/complejos", label: "Complejos", roles: ["administrador"] },
  { to: "/partidos", label: "Partidos", roles: ["administrador", "planillero"] },
  { to: "/sanciones", label: "Sanciones", roles: ["administrador"] },
];

/** Secciones visibles para un rol (`null` = sin sesión). */
export const seccionesPara = (rol) => SECCIONES.filter((s) => s.roles.includes(rol ?? ANONIMO));

/** Página a la que se entra por defecto según el rol. */
export const inicioPara = (rol) => seccionesPara(rol)[0]?.to ?? "/reportes";
