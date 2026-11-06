import { useEffect, useState } from "react";
import { listarEdiciones } from "../api/ediciones";
import { listarSanciones, crearSancion, modificarSancion, eliminarSancion } from "../api/sanciones";
import { useAuth } from "../auth/useAuth";

const ETIQUETA_MOTIVO = {
    roja: "Tarjeta roja",
    acumulacion_amarillas: "Acumulación de amarillas",
    disciplinaria: "Disciplinaria",
};

export default function Sanciones() {
    const { esAdmin } = useAuth();

    // Datos que vienen del backend
    const [ediciones, setEdiciones] = useState([]);
    const [idTorneo, setIdTorneo] = useState("");
    const [sanciones, setSanciones] = useState([]);

    // Mensaje de las acciones sobre la tabla (modificar, eliminar)
    const [mensajeTabla, setMensajeTabla] = useState("");
    const [errorTabla, setErrorTabla] = useState(false);

    // Formulario de nueva sanción disciplinaria
    const [ci, setCi] = useState("");
    const [fechaInicio, setFechaInicio] = useState("");
    const [cantidadFechas, setCantidadFechas] = useState("1");
    const [mensajeForm, setMensajeForm] = useState("");
    const [errorForm, setErrorForm] = useState(false);

    // Edición: la sanción que se está modificando (null si ninguna)
    const [editando, setEditando] = useState(null);
    const [editInicio, setEditInicio] = useState("");
    const [editCantidad, setEditCantidad] = useState("");

    // Al abrir la página: traer las ediciones y elegir la primera
    useEffect(() => {
        listarEdiciones().then((lista) => {
            setEdiciones(lista);
            if (lista.length > 0) setIdTorneo(lista[0].id_torneo);
        });
    }, []);

    // Cada vez que cambia la edición: traer sus sanciones
    const cargarSanciones = () => {
        listarSanciones(idTorneo).then(setSanciones);
    };

    useEffect(() => {
        if (!idTorneo) return;
        cargarSanciones();
        setMensajeForm("");
        setMensajeTabla("");
        setEditando(null);
    }, [idTorneo]);

    // Crear una sanción disciplinaria
    const enviarSancion = async (e) => {
        e.preventDefault();

        if (!ci || !fechaInicio || !cantidadFechas) {
            setErrorForm(true);
            setMensajeForm("Completá todos los campos");
            return;
        }

        try {
            await crearSancion({
                ci_jugador: ci.trim(),
                id_torneo: Number(idTorneo),
                motivo: "disciplinaria",
                numero_fecha_inicio: Number(fechaInicio),
                cantidad_fechas: Number(cantidadFechas),
            });
            setErrorForm(false);
            setMensajeForm("Sanción registrada");
            setCi("");
            setFechaInicio("");
            setCantidadFechas("1");
            cargarSanciones();
        } catch (err) {
            setErrorForm(true);
            setMensajeForm(err.message);
        }
    };

    // Abrir el formulario de edición con los datos de la fila
    const empezarEdicion = (s) => {
        setEditando(s);
        setEditInicio(String(s.numero_fecha_inicio));
        setEditCantidad(String(s.cantidad_fechas));
        setMensajeTabla("");
    };

    // Guardar los cambios (el motivo no se modifica)
    const guardarEdicion = async (e) => {
        e.preventDefault();

        try {
            await modificarSancion(editando.id_sancion, {
                motivo: editando.motivo,
                numero_fecha_inicio: Number(editInicio),
                cantidad_fechas: Number(editCantidad),
            });
            setErrorTabla(false);
            setMensajeTabla(`Sanción de ${editando.apellido}, ${editando.nombre} modificada`);
            setEditando(null);
            cargarSanciones();
        } catch (err) {
            setErrorTabla(true);
            setMensajeTabla(err.message);
        }
    };

    // Eliminar una sanción
    const eliminar = async (s) => {
        if (!window.confirm(`¿Eliminar la sanción de ${s.apellido}, ${s.nombre}?`)) return;

        try {
            await eliminarSancion(s.id_sancion);
            setErrorTabla(false);
            setMensajeTabla(`Sanción de ${s.apellido}, ${s.nombre} eliminada`);
            if (editando && editando.id_sancion === s.id_sancion) setEditando(null);
            cargarSanciones();
        } catch (err) {
            setErrorTabla(true);
            setMensajeTabla(err.message);
        }
    };

    return (
        <div>
            <div className="encabezado">
                <h2>Sanciones</h2>
            </div>

            <label className="selector-edicion">
                Edición:{" "}
                <select value={idTorneo} onChange={(e) => setIdTorneo(Number(e.target.value))}>
                    {ediciones.map((ed) => (
                        <option key={ed.id_torneo} value={ed.id_torneo}>{ed.nombre}</option>
                    ))}
                </select>
            </label>

            {/* Tabla de sanciones */}
            <div className="panel">
                <h3>Sanciones de la edición</h3>
                <p className="sub">
                    Las de tarjeta roja y acumulación de amarillas se generan automáticamente al registrar las tarjetas.
                </p>

                {mensajeTabla && <p className={errorTabla ? "error" : "aviso"}>{mensajeTabla}</p>}

                {sanciones.length === 0 ? (
                    <p className="vacio">Esta edición no tiene sanciones.</p>
                ) : (
                    <div className="tabla-scroll">
                        <table>
                            <thead>
                                <tr>
                                    <th>Jugador</th>
                                    <th>CI</th>
                                    <th>Motivo</th>
                                    <th>Desde la fecha</th>
                                    <th>Fechas</th>
                                    <th>Hasta la fecha</th>
                                    {esAdmin && <th>Acciones</th>}
                                </tr>
                            </thead>
                            <tbody>
                                {sanciones.map((s) => (
                                    <tr key={s.id_sancion}>
                                        <td>{s.apellido}, {s.nombre}</td>
                                        <td>{s.ci_jugador}</td>
                                        <td>{ETIQUETA_MOTIVO[s.motivo]}</td>
                                        <td>{s.numero_fecha_inicio}</td>
                                        <td>{s.cantidad_fechas}</td>
                                        <td>{s.numero_fecha_inicio + s.cantidad_fechas - 1}</td>
                                        {esAdmin && (
                                            <td>
                                                <div className="acciones">
                                                    <button className="btn" onClick={() => empezarEdicion(s)}>Editar</button>
                                                    <button className="btn btn-peligro" onClick={() => eliminar(s)}>Eliminar</button>
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

            {/* Editar sanción */}
            {esAdmin && editando && (
                <div className="panel">
                    <h3>Editar sanción de {editando.apellido}, {editando.nombre}</h3>
                    <p className="sub">Motivo: {ETIQUETA_MOTIVO[editando.motivo]}. El motivo no se puede cambiar.</p>

                    <form onSubmit={guardarEdicion}>
                        <div className="grilla-form">
                            <div className="campo">
                                <label htmlFor="editar-inicio">Desde la fecha</label>
                                <input
                                    id="editar-inicio"
                                    type="number"
                                    min="1"
                                    value={editInicio}
                                    onChange={(e) => setEditInicio(e.target.value)}
                                />
                            </div>

                            <div className="campo">
                                <label htmlFor="editar-cantidad">Cantidad de fechas</label>
                                <input
                                    id="editar-cantidad"
                                    type="number"
                                    min="1"
                                    value={editCantidad}
                                    onChange={(e) => setEditCantidad(e.target.value)}
                                />
                            </div>
                        </div>

                        <div className="modal-acciones">
                            <button type="button" className="btn" onClick={() => setEditando(null)}>Cancelar</button>
                            <button type="submit" className="btn btn-primario">Guardar cambios</button>
                        </div>
                    </form>
                </div>
            )}

            {/* Nueva sanción disciplinaria */}
            {esAdmin && (
                <div className="panel">
                    <h3>Nueva sanción disciplinaria</h3>
                    <p className="sub">
                        El jugador tiene que estar inscripto en un equipo de la edición elegida.
                    </p>

                    <form onSubmit={enviarSancion}>
                        <div className="grilla-form">
                            <div className="campo">
                                <label htmlFor="sancion-ci">Cédula del jugador</label>
                                <input
                                    id="sancion-ci"
                                    type="text"
                                    value={ci}
                                    onChange={(e) => setCi(e.target.value)}
                                />
                            </div>

                            <div className="campo">
                                <label htmlFor="sancion-inicio">Desde la fecha</label>
                                <input
                                    id="sancion-inicio"
                                    type="number"
                                    min="1"
                                    value={fechaInicio}
                                    onChange={(e) => setFechaInicio(e.target.value)}
                                />
                            </div>

                            <div className="campo">
                                <label htmlFor="sancion-cantidad">Cantidad de fechas</label>
                                <input
                                    id="sancion-cantidad"
                                    type="number"
                                    min="1"
                                    value={cantidadFechas}
                                    onChange={(e) => setCantidadFechas(e.target.value)}
                                />
                            </div>
                        </div>

                        <div className="modal-acciones">
                            <button type="submit" className="btn btn-primario">Registrar sanción</button>
                        </div>
                    </form>

                    {mensajeForm && <p className={errorForm ? "error" : "aviso"}>{mensajeForm}</p>}
                </div>
            )}
        </div>
    );
}