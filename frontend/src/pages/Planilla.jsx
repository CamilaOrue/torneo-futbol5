import { useState } from "react";
import { guardarPlanilla, guardarGoles, guardarTarjeta, eliminarGol } from "../api/planilla";

export default function Planilla() {

    // Estados de la planilla
    const [idPartido, setIdPartido] = useState("");
    const [cedulas, setCedulas] = useState("");
    const [mensaje, setMensaje] = useState("");

    // Estados del gol
    const [golPartido, setGolPartido] = useState("");
    const [golCi, setGolCi] = useState("");
    const [golMinuto, setGolMinuto] = useState("");
    const [autogol, setAutogol] = useState(false);
    const [mensajeGol, setMensajeGol] = useState("");

    // Estados de la tarjeta
    const [tarjetaPartido, setTarjetaPartido] = useState("");
    const [tarjetaCi, setTarjetaCi] = useState("");
    const [tarjetaMinuto, setTarjetaMinuto] = useState("");
    const [color, setColor] = useState("amarilla");
    const [mensajeTarjeta, setMensajeTarjeta] = useState("");

    // Estados de eliminar gol
    const [idGolEliminar, setIdGolEliminar] = useState("");
    const [mensajeEliminar, setMensajeEliminar] = useState("");

    // Guardar planilla
    const enviarPlanilla = async (e) => {
        e.preventDefault();

        const lista = cedulas.split(",").map((c) => c.trim()).filter((c) => c !== "");

        try {
            await guardarPlanilla(idPartido, { jugadores: lista });
            setMensaje("Planilla guardada");
        } catch (err) {
            setMensaje(err.message);
        }
    };

    // Guardar gol
    const enviarGol = async (e) => {
        e.preventDefault();

        try {
            const res = await guardarGoles(golPartido, {
                ci: golCi,
                minuto: Number(golMinuto),
                autogol: autogol
            });
            setMensajeGol(`Gol guardado (id ${res.id_gol})`);
            setGolCi("");
            setGolMinuto("");
            setAutogol(false);
        } catch (err) {
            setMensajeGol(err.message);
        }
    };

    // Guardar tarjeta
    const enviarTarjeta = async (e) => {
        e.preventDefault();

        try {
            await guardarTarjeta(tarjetaPartido, {
                ci: tarjetaCi,
                minuto: Number(tarjetaMinuto),
                color: color
            });
            setMensajeTarjeta("Tarjeta guardada");
            setTarjetaCi("");
            setTarjetaMinuto("");
        } catch (err) {
            setMensajeTarjeta(err.message);
        }
    };

    // Eliminar gol
    const enviarEliminarGol = async (e) => {
        e.preventDefault();

        try {
            await eliminarGol(idGolEliminar);
            setMensajeEliminar("Gol eliminado");
            setIdGolEliminar("");
        } catch (err) {
            setMensajeEliminar(err.message);
        }
    };

    return (
        <div>
            <h2>Planilla del partido</h2>

            <form onSubmit={enviarPlanilla}>
                <input
                    type="number"
                    placeholder="ID del partido"
                    value={idPartido}
                    onChange={(e) => setIdPartido(e.target.value)}
                />

                <input
                    type="text"
                    placeholder="Cédulas separadas por coma"
                    value={cedulas}
                    onChange={(e) => setCedulas(e.target.value)}
                />

                <button type="submit">Guardar</button>
            </form>

            {mensaje && <p>{mensaje}</p>}

            <hr />

            <h2>Registrar gol</h2>

            <form onSubmit={enviarGol}>
                <input
                    type="number"
                    placeholder="ID del partido"
                    value={golPartido}
                    onChange={(e) => setGolPartido(e.target.value)}
                />

                <input
                    type="text"
                    placeholder="Cédula del jugador"
                    value={golCi}
                    onChange={(e) => setGolCi(e.target.value)}
                />

                <input
                    type="number"
                    placeholder="Minuto"
                    value={golMinuto}
                    onChange={(e) => setGolMinuto(e.target.value)}
                />

                <label>
                    <input
                        type="checkbox"
                        checked={autogol}
                        onChange={(e) => setAutogol(e.target.checked)}
                    />
                    Autogol
                </label>

                <button type="submit">Registrar gol</button>
            </form>

            {mensajeGol && <p>{mensajeGol}</p>}

            <hr />

            <h2>Registrar tarjeta</h2>

            <form onSubmit={enviarTarjeta}>
                <input
                    type="number"
                    placeholder="ID del partido"
                    value={tarjetaPartido}
                    onChange={(e) => setTarjetaPartido(e.target.value)}
                />

                <input
                    type="text"
                    placeholder="Cédula del jugador"
                    value={tarjetaCi}
                    onChange={(e) => setTarjetaCi(e.target.value)}
                />

                <input
                    type="number"
                    placeholder="Minuto"
                    value={tarjetaMinuto}
                    onChange={(e) => setTarjetaMinuto(e.target.value)}
                />

                <select
                    value={color}
                    onChange={(e) => setColor(e.target.value)}
                >
                    <option value="amarilla">Amarilla</option>
                    <option value="roja">Roja</option>
                </select>

                <button type="submit">Registrar tarjeta</button>
            </form>

            {mensajeTarjeta && <p>{mensajeTarjeta}</p>}

            <hr />

            <h2>Eliminar gol</h2>

            <form onSubmit={enviarEliminarGol}>
                <input
                    type="number"
                    placeholder="ID del gol"
                    value={idGolEliminar}
                    onChange={(e) => setIdGolEliminar(e.target.value)}
                />

                <button type="submit">Eliminar gol</button>
            </form>

            {mensajeEliminar && <p>{mensajeEliminar}</p>}
        </div>
    );
}