import { useState } from "react";
import { guardarPlanilla, guardarGoles, guardarTarjeta } from "../api/planilla";

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

    // Enviar planilla
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

    // guardar gol
    const enviarGol = async (e) => {
        e.preventDefault();

        try {
            await guardarGoles(golPartido, {
                ci: golCi,
                minuto: Number(golMinuto),
                autogol: autogol
            });
            setMensajeGol("Gol guardado");
        } catch (err) {
            setMensajeGol(err.message);
        }
    };

    // guardar tarjeta
    const enviarTarjeta = async (e) => {
        e.preventDefault();

        try {
            await guardarTarjeta(tarjetaPartido, {
                ci: tarjetaCi,
                minuto: Number(tarjetaMinuto),
                color: color
            });
            setMensajeTarjeta("Tarjeta guardada");
        } catch (err) {
            setMensajeTarjeta(err.message);
        }
    };

    return (
        <div>
            <h2>Guardar planilla</h2>

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

                <button type="submit">Guardar planilla</button>
            </form>

            {mensaje && <p>{mensaje}</p>}

            <hr />

            <h2>guardar gol</h2>

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

                <button type="submit">guardar gol</button>
            </form>

            {mensajeGol && <p>{mensajeGol}</p>}

            <hr />

            <h2>guardar tarjeta</h2>

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

                <button type="submit">guardar tarjeta</button>
            </form>

            {mensajeTarjeta && <p>{mensajeTarjeta}</p>}
        </div>
    );
}