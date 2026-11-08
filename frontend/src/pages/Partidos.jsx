import { useEffect, useState } from "react";
import { listarEdiciones } from "../api/ediciones";
import { listarEquipos } from "../api/equipos";
import {
    listarPartidos,
    crearPartido,
    cambiarEstadoPartido,
    eliminarPartido,
    listarCanchas,
    modificarPartido,
} from "../api/partidos";
import { formatFecha } from "../utils";
import { useAuth } from "../auth/useAuth";

// Los turnos son fijos (vienen del seed) y no hay endpoint para listarlos
const TURNOS = {
    1: "18:00",
    2: "19:00",
    3: "20:00",
    4: "21:00",
    5: "22:00",
};

const ETIQUETA_ESTADO_PARTIDO = {
    programado: "Programado",
    jugado: "Jugado",
    postergado: "Postergado",
    cancelado: "Cancelado",
};

export default function Partidos() {
    const { rol } = useAuth();

    // Datos que vienen del backend
    const [ediciones, setEdiciones] = useState([]);
    const [idTorneo, setIdTorneo] = useState("");
    const [partidos, setPartidos] = useState([]);
    const [equipos, setEquipos] = useState([]);
    const [canchas, setCanchas] = useState([]);

    // Mensaje de las acciones sobre la tabla (cambiar estado, eliminar)
    const [mensajeTabla, setMensajeTabla] = useState("");
    const [errorTabla, setErrorTabla] = useState(false);

    // Formulario para programar un partido
    const [numeroFecha, setNumeroFecha] = useState("");
    const [local, setLocal] = useState("");
    const [visitante, setVisitante] = useState("");
    const [dia, setDia] = useState("");
    const [turno, setTurno] = useState("1");
    const [cancha, setCancha] = useState("");
    const [mensajeForm, setMensajeForm] = useState("");
    const [errorForm, setErrorForm] = useState(false);

    // Reprogramación: el partido que se está reprogramando (null si ninguno)
    const [reprogramando, setReprogramando] = useState(null);
    const [repFecha, setRepFecha] = useState("");
    const [repDia, setRepDia] = useState("");
    const [repTurno, setRepTurno] = useState("1");
    const [repCancha, setRepCancha] = useState("");

    // Al abrir la página: traer las ediciones y las canchas
    useEffect(() => {
        listarEdiciones().then((lista) => {
            setEdiciones(lista);
            if (lista.length > 0) setIdTorneo(lista[0].id_torneo);
        });
        listarCanchas().then(setCanchas);
    }, []);

    // Cada vez que cambia la edición: traer sus partidos y sus equipos
    const cargarPartidos = () => {
        listarPartidos(idTorneo).then(setPartidos);
    };

    useEffect(() => {
        if (!idTorneo) return;
        cargarPartidos();
        if (rol === "administrador") {
            listarEquipos(idTorneo).then(setEquipos);
        }
        setMensajeTabla("");
        setMensajeForm("");
        setReprogramando(null);
    }, [idTorneo]);

    // El backend devuelve los equipos por id: esto los traduce al nombre
    const nombreEquipo = (id) => {
        const equipo = equipos.find((e) => e.id_equipo === id);
        return equipo ? equipo.nombre : `Equipo ${id}`;
    };

    const nombreCancha = (p) => {
        const c = canchas.find(
            (c) => c.id_complejo === p.id_complejo && c.nombre_cancha === p.nombre_cancha
        );
        return c ? `${c.nombre_cancha} (${c.nombre_complejo})` : p.nombre_cancha;
    };

    // Cambiar el estado de un partido
    const cambiarEstado = async (idPartido, estado) => {
        try {
            await cambiarEstadoPartido(idPartido, estado);
            setErrorTabla(false);
            setMensajeTabla(`Partido ${idPartido}: ${ETIQUETA_ESTADO_PARTIDO[estado].toLowerCase()}`);
            cargarPartidos();
        } catch (err) {
            setErrorTabla(true);
            setMensajeTabla(err.message);
        }
    };

    // Eliminar un partido
    const eliminar = async (idPartido) => {
        if (!window.confirm(`¿Eliminar el partido ${idPartido}?`)) return;

        try {
            await eliminarPartido(idPartido);
            setErrorTabla(false);
            setMensajeTabla(`Partido ${idPartido} eliminado`);
            cargarPartidos();
        } catch (err) {
            setErrorTabla(true);
            setMensajeTabla(err.message);
        }
    };

    // Abrir el formulario de reprogramación con los datos actuales del partido
    const empezarReprogramacion = (p) => {
        setReprogramando(p);
        setRepFecha(String(p.numero_fecha));
        setRepDia(p.dia);
        setRepTurno(String(p.id_turno));
        setRepCancha(`${p.id_complejo}|${p.nombre_cancha}`);
        setMensajeTabla("");
    };

    // Guardar la reprogramación (los equipos no cambian)
    const guardarReprogramacion = async (e) => {
        e.preventDefault();

        if (!repFecha || !repDia || !repCancha) {
            setErrorTabla(true);
            setMensajeTabla("Completá todos los campos de la reprogramación");
            return;
        }

        const [idComplejo, nombreCanchaElegida] = repCancha.split("|");

        try {
            await modificarPartido(reprogramando.id_partido, {
                numero_fecha: Number(repFecha),
                dia: repDia,
                id_turno: Number(repTurno),
                nombre_cancha: nombreCanchaElegida,
                id_complejo: Number(idComplejo),
            });
            setErrorTabla(false);
            setMensajeTabla(`Partido ${reprogramando.id_partido} reprogramado`);
            setReprogramando(null);
            cargarPartidos();
        } catch (err) {
            setErrorTabla(true);
            setMensajeTabla(err.message);
        }
    };

    // Programar un partido nuevo
    const enviarPartido = async (e) => {
        e.preventDefault();

        if (!numeroFecha || !dia || !local || !visitante || !cancha) {
            setErrorForm(true);
            setMensajeForm("Completá todos los campos");
            return;
        }

        // La cancha se elige como "idComplejo|nombreCancha"
        const [idComplejo, nombreCanchaElegida] = cancha.split("|");

        try {
            await crearPartido({
                id_torneo: Number(idTorneo),
                numero_fecha: Number(numeroFecha),
                id_equipo_local: Number(local),
                id_equipo_visitante: Number(visitante),
                dia: dia,
                id_turno: Number(turno),
                nombre_cancha: nombreCanchaElegida,
                id_complejo: Number(idComplejo),
            });
            setErrorForm(false);
            setMensajeForm("Partido programado");
            setLocal("");
            setVisitante("");
            cargarPartidos();
        } catch (err) {
            setErrorForm(true);
            setMensajeForm(err.message);
        }
    };

    return (
        <div>
            <div className="encabezado">
                <h2>Partidos</h2>
            </div>

            <label className="selector-edicion">
                Edición:{" "}
                <select value={idTorneo} onChange={(e) => setIdTorneo(Number(e.target.value))}>
                    {ediciones.map((ed) => (
                        <option key={ed.id_torneo} value={ed.id_torneo}>{ed.nombre}</option>
                    ))}
                </select>
            </label>

            {/* Fixture */}
            <div className="panel">
                <h3>Fixture</h3>
                <p className="sub">Partidos de la edición, ordenados por día y hora.</p>

                {mensajeTabla && <p className={errorTabla ? "error" : "aviso"}>{mensajeTabla}</p>}

                {partidos.length === 0 ? (
                    <p className="vacio">Esta edición no tiene partidos.</p>
                ) : (
                    <div className="tabla-scroll">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Fecha</th>
                                    <th>Día</th>
                                    <th>Hora</th>
                                    <th>Local</th>
                                    <th>Visitante</th>
                                    <th>Cancha</th>
                                    <th>Estado</th>
                                    {rol === "administrador" && (
                                        <th>Acciones</th>
                                    )}
                                </tr>
                            </thead>
                            <tbody>
                                {partidos.map((p) => (
                                    <tr key={p.id_partido}>
                                        <td>{p.id_partido}</td>
                                        <td>{p.numero_fecha}</td>
                                        <td>{formatFecha(p.dia)}</td>
                                        <td>{TURNOS[p.id_turno] ?? `Turno ${p.id_turno}`}</td>
                                        <td>{nombreEquipo(p.id_equipo_local)}</td>
                                        <td>{nombreEquipo(p.id_equipo_visitante)}</td>
                                        <td>{nombreCancha(p)}</td>
                                        <td>{ETIQUETA_ESTADO_PARTIDO[p.estado]}</td>
                                        {rol === "administrador" && (
                                            <td>
                                                <div className="acciones">
                                                    {p.estado === "programado" && (
                                                        <>
                                                            <button className="btn btn-primario" onClick={() => cambiarEstado(p.id_partido, "jugado")}>Jugado</button>
                                                            <button className="btn" onClick={() => cambiarEstado(p.id_partido, "postergado")}>Postergar</button>
                                                        </>
                                                    )}
                                                                                                    {p.estado === "postergado" && (
                                                        <button className="btn" onClick={() => empezarReprogramacion(p)}>Reprogramar</button>
                                                    )}
                                                    {(p.estado === "programado" || p.estado === "postergado") && (
                                                        <button className="btn" onClick={() => cambiarEstado(p.id_partido, "cancelado")}>Cancelar</button>
                                                    )}
                                                    {p.estado !== "jugado" && (
                                                        <button className="btn btn-peligro" onClick={() => eliminar(p.id_partido)}>Eliminar</button>
                                                    )}
                                                </div>
                                            </td>
                                        )}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {rol === "administrador" && (
                <>
                    {/* Reprogramar partido */}
                    {reprogramando && (
                        <div className="panel">
                            <h3>
                                Reprogramar partido {reprogramando.id_partido}: {nombreEquipo(reprogramando.id_equipo_local)} vs{" "}
                                {nombreEquipo(reprogramando.id_equipo_visitante)}
                            </h3>
                            <p className="sub">
                                Se cambian el día, el turno y la cancha; los equipos no. Si estaba postergado, vuelve a programado.
                            </p>
    
                            <form onSubmit={guardarReprogramacion}>
                                <div className="grilla-form">
                                    <div className="campo">
                                        <label htmlFor="rep-fecha">Número de fecha</label>
                                        <input
                                            id="rep-fecha"
                                            type="number"
                                            min="1"
                                            value={repFecha}
                                            disabled
                                        />
                                    </div>
    
                                    <div className="campo">
                                        <label htmlFor="rep-dia">Día</label>
                                        <input
                                            id="rep-dia"
                                            type="date"
                                            value={repDia}
                                            onChange={(e) => setRepDia(e.target.value)}
                                        />
                                    </div>
    
                                    <div className="campo">
                                        <label htmlFor="rep-turno">Turno</label>
                                        <select id="rep-turno" value={repTurno} onChange={(e) => setRepTurno(e.target.value)}>
                                            {Object.entries(TURNOS).map(([id, hora]) => (
                                                <option key={id} value={id}>{hora}</option>
                                            ))}
                                        </select>
                                    </div>
    
                                    <div className="campo">
                                        <label htmlFor="rep-cancha">Cancha</label>
                                        <select id="rep-cancha" value={repCancha} onChange={(e) => setRepCancha(e.target.value)}>
                                            <option value="">Elegí una cancha</option>
                                            {canchas.map((c) => (
                                                <option key={`${c.id_complejo}|${c.nombre_cancha}`} value={`${c.id_complejo}|${c.nombre_cancha}`}>
                                                    {c.nombre_cancha} ({c.nombre_complejo})
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                </div>
    
                                <div className="modal-acciones">
                                    <button type="button" className="btn" onClick={() => setReprogramando(null)}>Cancelar</button>
                                    <button type="submit" className="btn btn-primario">Guardar reprogramación</button>
                                </div>
                            </form>
                        </div>
                    )}
    
                    {/* Programar partido */}
                    <div className="panel">
                        <h3>Programar partido</h3>
                        <p className="sub">Los dos equipos tienen que ser de la edición elegida. La cancha no puede estar ocupada en ese día y turno.</p>
    
                        <form onSubmit={enviarPartido}>
                            <div className="grilla-form">
                                <div className="campo">
                                    <label htmlFor="partido-fecha">Número de fecha</label>
                                    <input
                                        id="partido-fecha"
                                        type="number"
                                        min="1"
                                        value={numeroFecha}
                                        onChange={(e) => setNumeroFecha(e.target.value)}
                                    />
                                </div>
    
                                <div className="campo">
                                    <label htmlFor="partido-dia">Día</label>
                                    <input
                                        id="partido-dia"
                                        type="date"
                                        value={dia}
                                        onChange={(e) => setDia(e.target.value)}
                                    />
                                </div>
    
                                <div className="campo">
                                    <label htmlFor="partido-local">Local</label>
                                    <select id="partido-local" value={local} onChange={(e) => setLocal(e.target.value)}>
                                        <option value="">Elegí un equipo</option>
                                        {equipos.map((eq) => (
                                            <option key={eq.id_equipo} value={eq.id_equipo}>{eq.nombre}</option>
                                        ))}
                                    </select>
                                </div>
    
                                <div className="campo">
                                    <label htmlFor="partido-visitante">Visitante</label>
                                    <select id="partido-visitante" value={visitante} onChange={(e) => setVisitante(e.target.value)}>
                                        <option value="">Elegí un equipo</option>
                                        {equipos.map((eq) => (
                                            <option key={eq.id_equipo} value={eq.id_equipo}>{eq.nombre}</option>
                                        ))}
                                    </select>
                                </div>
    
                                <div className="campo">
                                    <label htmlFor="partido-turno">Turno</label>
                                    <select id="partido-turno" value={turno} onChange={(e) => setTurno(e.target.value)}>
                                        {Object.entries(TURNOS).map(([id, hora]) => (
                                            <option key={id} value={id}>{hora}</option>
                                        ))}
                                    </select>
                                </div>
    
                                <div className="campo">
                                    <label htmlFor="partido-cancha">Cancha</label>
                                    <select id="partido-cancha" value={cancha} onChange={(e) => setCancha(e.target.value)}>
                                        <option value="">Elegí una cancha</option>
                                        {canchas.map((c) => (
                                            <option key={`${c.id_complejo}|${c.nombre_cancha}`} value={`${c.id_complejo}|${c.nombre_cancha}`}>
                                                {c.nombre_cancha} ({c.nombre_complejo})
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>
    
                            <div className="modal-acciones">
                                <button type="submit" className="btn btn-primario">Programar partido</button>
                            </div>
                        </form>
    
                        {mensajeForm && <p className={errorForm ? "error" : "aviso"}>{mensajeForm}</p>}
                    </div>
                </>
            )}
        </div>
    );
}