/** Muestra carga / error y, cuando hay datos, ejecuta children(data). */
export default function Estado({ loading, error, data, children }) {
  if (error)
    return (
      <p className="error" role="alert">
        {error}
      </p>
    );
  if (loading && !data) return <p className="cargando">Cargando…</p>;
  return children(data);
}
