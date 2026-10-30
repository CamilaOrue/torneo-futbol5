/**
 * Tabla genérica.
 * columns: [{ key, label, render?(fila) }]
 * onRowClick (opcional) hace clickeables las filas; selectedKey marca la activa.
 */
export default function DataTable({
  columns,
  rows,
  rowKey,
  onRowClick,
  selectedKey,
  vacio = "No hay resultados.",
}) {
  if (!rows.length) return <p className="vacio">{vacio}</p>;

  return (
    <div className="tabla-scroll">
      <table>
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c.key}>{c.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((fila) => {
            const k = fila[rowKey];
            const clickeable = Boolean(onRowClick);
            return (
              <tr
                key={k}
                className={[clickeable && "clickeable", k === selectedKey && "seleccionada"]
                  .filter(Boolean)
                  .join(" ")}
                onClick={clickeable ? () => onRowClick(fila) : undefined}
                onKeyDown={
                  clickeable
                    ? (e) => (e.key === "Enter" || e.key === " ") && onRowClick(fila)
                    : undefined
                }
                tabIndex={clickeable ? 0 : undefined}
              >
                {columns.map((c) => (
                  <td key={c.key}>{c.render ? c.render(fila) : fila[c.key]}</td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
