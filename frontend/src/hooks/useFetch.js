import { useEffect, useState } from "react";

/**
 * Ejecuta `fetcher` al montar y cada vez que cambian `deps`.
 * Mientras recarga conserva los datos anteriores (evita parpadeos al filtrar).
 */
export function useFetch(fetcher, deps = []) {
  const [state, setState] = useState({ data: null, loading: true, error: null });

  useEffect(() => {
    let cancelado = false;
    setState((s) => ({ ...s, loading: true, error: null }));
    fetcher()
      .then((data) => !cancelado && setState({ data, loading: false, error: null }))
      .catch((e) => !cancelado && setState({ data: null, loading: false, error: e.message }));
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return state;
}
