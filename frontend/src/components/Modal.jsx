import { useEffect, useId } from "react";

/** Ventana modal accesible: se cierra con Escape o haciendo clic fuera. */
export default function Modal({ titulo, onClose, children }) {
  const tituloId = useId();

  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="overlay" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby={tituloId}>
        <h3 id={tituloId}>{titulo}</h3>
        {children}
      </div>
    </div>
  );
}
