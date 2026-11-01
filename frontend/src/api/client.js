const BASE = "/api";

/** Error de la API. `fields` mapea nombre de campo -> mensaje (errores 422/409 asociados a un campo). */
export class ApiError extends Error {
  constructor(message, status, fields = {}) {
    super(message);
    this.status = status;
    this.fields = fields;
  }
}

const TRADUCCIONES = [
  [/^Field required/, "Este campo es obligatorio"],
  [/^Input should be a valid date/, "La fecha no es válida"],
  [/^Input should be a valid integer/, "Debe ser un número entero"],
];

function limpiar(msg) {
  const sinPrefijo = msg.replace(/^Value error, /, "");
  for (const [patron, texto] of TRADUCCIONES) if (patron.test(sinPrefijo)) return texto;
  return sinPrefijo;
}

async function request(method, path, body) {
  const token = localStorage.getItem("token");
  let res;
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError("No se pudo contactar al servidor", 0);
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    let mensaje;
    const fields = {};
    if (Array.isArray(err.detail)) {
      // FastAPI: [{ loc: ["body", "campo"], msg }, ...]
      err.detail.forEach((e) => {
        const campo = e.loc?.[0] === "body" ? e.loc[1] : undefined;
        if (campo !== undefined && !(campo in fields)) fields[campo] = limpiar(e.msg);
      });
      mensaje = err.detail.map((e) => limpiar(e.msg)).join(". ");
    } else {
      mensaje = err.detail;
    }
    throw new ApiError(mensaje || `Error ${res.status}`, res.status, fields);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  get: (p) => request("GET", p),
  post: (p, b) => request("POST", p, b),
  put: (p, b) => request("PUT", p, b),
  delete: (p) => request("DELETE", p),
};

/** Arma un query string ignorando valores vacíos. */
export function query(params) {
  const sp = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") sp.set(k, v);
  });
  const s = sp.toString();
  return s ? `?${s}` : "";
}
