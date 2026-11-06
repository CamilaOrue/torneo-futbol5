import { useState } from "react";
import { guardarPlanilla, guardarGoles, guardarTarjeta, eliminarGol } from "../api/planilla";

export default function Planilla() {

    // Estados de la planilla
    const [idPartido, setIdPartido] = useState("");
    const [cedulas, setCedulas] = useState("");
    const [mensaje, setMensaje] = useState("");
    const [errorPlanilla, setErrorPlanilla] = useState(false);

    // Estados del gol
    const [golPartido, setGolPartido] = useState("");
    const [golCi, setGolCi] = useState("");
    const [golMinuto, setGolMinuto] = useState("");
    const [autogol, setAutogol] = useState(false);
    const [mensajeGol, setMensajeGol] = useState("");
    const [errorGol, setErrorGol] = useState(false);

    // Estados de la tarjeta
    const [tarjetaPartido, setTarjetaPartido] = useState("");
    const [tarjetaCi, setTarjetaCi] = useState("");
    const [tarjetaMinuto, setTarjetaMinuto] = useState("");
    const [color, setColor] = useState("amarilla");
    const [mensajeTarjeta, setMensajeTarjeta] = useState("");
    const [errorTarjeta, setErrorTarjeta] = useState(false);

    // Estados de eliminar gol
    const [idGolEliminar, setIdGolEliminar] = useState("");
    const [mensajeEliminar, setMensajeEliminar] = useState("");
    const [errorEliminar, setErrorEliminar] = useState(false);

    // Guardar planilla
    const enviarPlanilla = async (e) => {
        e.preventDefault();

        const lista = cedulas.split(",").map((c) => c.trim()).filter((c) => c !== "");

        try {
            await guardarPlanilla(idPartido, { ci_jugadores: lista });
            setErrorPlanilla(false);
            setMensaje("Planilla guardada");
        } catch (err) {
            setErrorPlanilla(true);
            setMensaje(err.message);
        }
    };

    // Guardar gol
    const enviarGol = async (e) => {
        e.preventDefault();

        try {
            const res = await guardarGoles(golPartido, {
                ci_jugador: golCi,
                minuto: Number(golMinuto),
                autogol: autogol
            });
            setErrorGol(false);
            setMensajeGol(`Gol guardado (id ${res.id_gol})`);
            setGolCi("");
            setGolMinuto("");
            setAutogol(false);
        } catch (err) {
            setErrorGol(true);
            setMensajeGol(err.message);
        }
    };

    // Guardar tarjeta
    const enviarTarjeta = async (e) => {
        e.preventDefault();

        try {
            await guardarTarjeta(tarjetaPartido, {
                ci_jugador: tarjetaCi,
                minuto: Number(tarjetaMinuto),
                color: color
            });
            setErrorTarjeta(false);
            setMensajeTarjeta("Tarjeta guardada");
            setTarjetaCi("");
            setTarjetaMinuto("");
        } catch (err) {
            setErrorTarjeta(true);
            setMensajeTarjeta(err.message);
        }
    };

    // Eliminar gol
    const enviarEliminarGol = async (e) => {
        e.preventDefault();

        try {
            await eliminarGol(idGolEliminar);
            setErrorEliminar(false);
            setMensajeEliminar("Gol eliminado");
            setIdGolEliminar("");
        } catch (err) {
            setErrorEliminar(true);
            setMensajeEliminar(err.message);
        }
    };

    return (
        <div>
            <div className="encabezado">
                <h2>Planilla</h2>
            </div>

            {/* Planilla */}
            <div className="panel">
                <h3>Jugadores del partido</h3>
                <p className="sub">Cédulas de los jugadores que participaron, de los dos equipos, separadas por coma.</p>

                <form onSubmit={enviarPlanilla}>
                    <div className="grilla-form">
                        <div className="campo">
                            <label htmlFor="planilla-partido">ID del partido</label>
                            <input
                                id="planilla-partido"
                                type="number"
                                value={idPartido}
                                onChange={(e) => setIdPartido(e.target.value)}
                            />
                        </div>

                        <div className="campo">
                            <label htmlFor="planilla-cedulas">Cédulas</label>
                            <input
                                id="planilla-cedulas"
                                type="text"
                                placeholder="45678901, 41234567, ..."
                                value={cedulas}
                                onChange={(e) => setCedulas(e.target.value)}
                            />
                        </div>
                    </div>

                    <div className="modal-acciones">
                        <button type="submit" className="btn btn-primario">Guardar planilla</button>
                    </div>
                </form>

                {mensaje && <p className={errorPlanilla ? "error" : "aviso"}>{mensaje}</p>}
            </div>

            {/* Gol */}
            <div className="panel">
                <h3>Registrar gol</h3>
                <p className="sub">El jugador tiene que estar en la planilla del partido.</p>

                <form onSubmit={enviarGol}>
                    <div className="grilla-form">
                        <div className="campo">
                            <label htmlFor="gol-partido">ID del partido</label>
                            <input
                                id="gol-partido"
                                type="number"
                                value={golPartido}
                                onChange={(e) => setGolPartido(e.target.value)}
                            />
                        </div>

                        <div className="campo">
                            <label htmlFor="gol-ci">Cédula del jugador</label>
                            <input
                                id="gol-ci"
                                type="text"
                                value={golCi}
                                onChange={(e) => setGolCi(e.target.value)}
                            />
                        </div>

                        <div className="campo">
                            <label htmlFor="gol-minuto">Minuto</label>
                            <input
                                id="gol-minuto"
                                type="number"
                                min="0"
                                max="60"
                                value={golMinuto}
                                onChange={(e) => setGolMinuto(e.target.value)}
                            />
                        </div>

                        <div className="campo">
                            <label htmlFor="gol-autogol">Autogol</label>
                            <input
                                id="gol-autogol"
                                type="checkbox"
                                checked={autogol}
                                onChange={(e) => setAutogol(e.target.checked)}
                            />
                        </div>
                    </div>

                    <div className="modal-acciones">
                        <button type="submit" className="btn btn-primario">Registrar gol</button>
                    </div>
                </form>

                {mensajeGol && <p className={errorGol ? "error" : "aviso"}>{mensajeGol}</p>}
            </div>

            {/* Tarjeta */}
            <div className="panel">
                <h3>Registrar tarjeta</h3>
                <p className="sub">Una roja, o cada tercera amarilla, genera automáticamente una sanción para la fecha siguiente.</p>

                <form onSubmit={enviarTarjeta}>
                    <div className="grilla-form">
                        <div className="campo">
                            <label htmlFor="tarjeta-partido">ID del partido</label>
                            <input
                                id="tarjeta-partido"
                                type="number"
                                value={tarjetaPartido}
                                onChange={(e) => setTarjetaPartido(e.target.value)}
                            />
                        </div>

                        <div className="campo">
                            <label htmlFor="tarjeta-ci">Cédula del jugador</label>
                            <input
                                id="tarjeta-ci"
                                type="text"
                                value={tarjetaCi}
                                onChange={(e) => setTarjetaCi(e.target.value)}
                            />
                        </div>

                        <div className="campo">
                            <label htmlFor="tarjeta-minuto">Minuto</label>
                            <input
                                id="tarjeta-minuto"
                                type="number"
                                min="0"
                                max="60"
                                value={tarjetaMinuto}
                                onChange={(e) => setTarjetaMinuto(e.target.value)}
                            />
                        </div>

                        <div className="campo">
                            <label htmlFor="tarjeta-color">Color</label>
                            <select
                                id="tarjeta-color"
                                value={color}
                                onChange={(e) => setColor(e.target.value)}
                            >
                                <option value="amarilla">Amarilla</option>
                                <option value="roja">Roja</option>
                            </select>
                        </div>
                    </div>

                    <div className="modal-acciones">
                        <button type="submit" className="btn btn-primario">Registrar tarjeta</button>
                    </div>
                </form>

                {mensajeTarjeta && <p className={errorTarjeta ? "error" : "aviso"}>{mensajeTarjeta}</p>}
            </div>

            {/* Eliminar gol */}
            <div className="panel">
                <h3>Eliminar gol</h3>
                <p className="sub">Solo dentro de las 48 horas posteriores al partido. El id aparece al registrar el gol.</p>

                <form onSubmit={enviarEliminarGol}>
                    <div className="grilla-form">
                        <div className="campo">
                            <label htmlFor="eliminar-gol">ID del gol</label>
                            <input
                                id="eliminar-gol"
                                type="number"
                                value={idGolEliminar}
                                onChange={(e) => setIdGolEliminar(e.target.value)}
                            />
                        </div>
                    </div>

                    <div className="modal-acciones">
                        <button type="submit" className="btn btn-peligro">Eliminar gol</button>
                    </div>
                </form>

                {mensajeEliminar && <p className={errorEliminar ? "error" : "aviso"}>{mensajeEliminar}</p>}
            </div>
        </div>
    );
}