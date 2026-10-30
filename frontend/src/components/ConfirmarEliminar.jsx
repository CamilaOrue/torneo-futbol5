import { useState } from "react";
import Modal from "./Modal";

/** Confirmación de baja. `onConfirmar` debe devolver una promesa; si falla se muestra el error. */
export default function ConfirmarEliminar({ titulo, children, onConfirmar, onCancelar }) {
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState(null);

  async function confirmar() {
    setEnviando(true);
    setError(null);
    try {
      await onConfirmar();
    } catch (e) {
      setError(e.message);
      setEnviando(false);
    }
  }

  return (
    <Modal titulo={titulo} onClose={onCancelar}>
      <p>{children}</p>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      <div className="modal-acciones">
        <button type="button" className="btn" onClick={onCancelar}>
          Cancelar
        </button>
        <button type="button" className="btn btn-peligro" onClick={confirmar} disabled={enviando}>
          {enviando ? "Eliminando…" : "Eliminar"}
        </button>
      </div>
    </Modal>
  );
}
