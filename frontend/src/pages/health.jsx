import { useEffect, useState } from "react";

export default function Health() {
  const [estado, setEstado] = useState("Consultando...");

  useEffect(() => {
    fetch("/api/health/db")
      .then((r) => r.json())
      .then((d) => setEstado(d.db ? "Backend y base OK ✅" : "Base sin respuesta ❌"))
      .catch(() => setEstado("No se pudo contactar al backend ❌"));
  }, []);

  return (
    <main style={{ padding: 24 }}>
      <h1>Torneo Interfacultades de Fútbol 5</h1>
      <p>{estado}</p>
    </main>
  );
}