import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { listarEdiciones, crearEdicion, cambiarEstadoEdicion } from "../api/ediciones";
import { useAuth } from "../auth/useAuth";
import DataTable from "../components/DataTable";
import Estado from "../components/Estado";
import { useFetch } from "../hooks/useFetch";
import { ETIQUETA_ESTADO, formatFecha } from "../utils";

// A qué estado puede avanzar cada edición, y el texto del botón
const SIGUIENTE_ESTADO = {
  inscripcion: { estado: "en curso", boton: "Iniciar torneo" },
  "en curso": { estado: "finalizado", boton: "Finalizar" },
};

export default function Ediciones() {
  const navigate = useNavigate();
  const { esAdmin } = useAuth();

  // Al cambiar "recarga", useFetch vuelve a pedir la lista
  const [recarga, setRecarga] = useState(0);
  const state = useFetch(listarEdiciones, [recarga]);

  // Mensaje de las acciones sobre la tabla
  const [mensajeTabla, setMensajeTabla] = useState("");
  const [errorTabla, setErrorTabla] = useState(false);

  // Formulario de nueva edición
  const [nombre, setNombre] = useState("");
  const [anio, setAnio] = useState("");
  const [semestre, setSemestre] = useState("1");
  const [fechaInicio, setFechaInicio] = useState("");
  const [fechaFin, setFechaFin] = useState("");
  const [mensajeForm, setMensajeForm] = useState("");
  const [errorForm, setErrorForm] = useState(false);

  const avanzarEstado = async (t) => {
    const siguiente = SIGUIENTE_ESTADO[t.estado];
    if (!window.confirm(`¿${siguiente.boton} "${t.nombre}"?`)) return;

    try {
      await cambiarEstadoEdicion(t.id_torneo, siguiente.estado);
      setErrorTabla(false);
      setMensajeTabla(`"${t.nombre}" pasó a ${ETIQUETA_ESTADO[siguiente.estado].toLowerCase()}`);
      setRecarga(recarga + 1);
    } catch (err) {
      setErrorTabla(true);
      setMensajeTabla(err.message);
    }
  };

  const enviarEdicion = async (e) => {
    e.preventDefault();

    if (!nombre || !anio || !fechaInicio || !fechaFin) {
      setErrorForm(true);
      setMensajeForm("Completá todos los campos");
      return;
    }

    try {
      await crearEdicion({
        nombre: nombre,
        anio: Number(anio),
        semestre: Number(semestre),
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
      });
      setErrorForm(false);
      setMensajeForm("Edición creada en etapa de inscripción");
      setNombre("");
      setAnio("");
      setFechaInicio("");
      setFechaFin("");
      setRecarga(recarga + 1);
    } catch (err) {
      setErrorForm(true);
      setMensajeForm(err.message);
    }
  };

  const columns = [
    { key: "nombre", label: "Edición" },
    { key: "periodo", label: "Semestre", render: (t) => `${t.anio} · S${t.semestre}` },
    {
      key: "fechas",
      label: "Fechas",
      render: (t) => `${formatFecha(t.fecha_inicio)} – ${formatFecha(t.fecha_fin)}`,
    },
    {
      key: "estado",
      label: "Estado",
      render: (t) => (
        <span className={`badge badge-${t.estado.replace(" ", "-")}`}>
          {ETIQUETA_ESTADO[t.estado]}
        </span>
      ),
    },
    { key: "cantidad_equipos", label: "Equipos" },
    {
      key: "partidos",
      label: "Partidos jugados",
      render: (t) => `${t.partidos_jugados} / ${t.cantidad_partidos}`,
    },
    {
      key: "acciones",
      label: "",
      render: (t) => (
        <div className="acciones">
          <button
            className="link"
            onClick={() => navigate(`/equipos?torneo=${t.id_torneo}`)}
          >
            Ver equipos
          </button>
          {esAdmin && SIGUIENTE_ESTADO[t.estado] && (
            <button className="link" onClick={() => avanzarEstado(t)}>
              {SIGUIENTE_ESTADO[t.estado].boton}
            </button>
          )}
        </div>
      ),
    },
  ];

  return (
    <section>
      <h2>Ediciones</h2>

      {mensajeTabla && <p className={errorTabla ? "error" : "aviso"}>{mensajeTabla}</p>}

      <Estado {...state}>
        {(ediciones) => (
          <DataTable
            columns={columns}
            rows={ediciones}
            rowKey="id_torneo"
            vacio="Todavía no hay ediciones cargadas."
          />
        )}
      </Estado>

      {esAdmin && (
        <div className="panel">
          <h3>Nueva edición</h3>
          <p className="sub">
            La edición se crea en etapa de inscripción: ahí se inscriben los equipos y se arman los planteles.
            Después se inicia el torneo y se arma el fixture.
          </p>

          <form onSubmit={enviarEdicion}>
            <div className="grilla-form">
              <div className="campo">
                <label htmlFor="edicion-nombre">Nombre</label>
                <input
                  id="edicion-nombre"
                  type="text"
                  maxLength={100}
                  placeholder="Torneo Interfacultades de Fútbol 5 – 2027 S1"
                  value={nombre}
                  onChange={(e) => setNombre(e.target.value)}
                />
              </div>

              <div className="campo">
                <label htmlFor="edicion-anio">Año</label>
                <input
                  id="edicion-anio"
                  type="number"
                  min="2000"
                  max="2100"
                  value={anio}
                  onChange={(e) => setAnio(e.target.value)}
                />
              </div>

              <div className="campo">
                <label htmlFor="edicion-semestre">Semestre</label>
                <select
                  id="edicion-semestre"
                  value={semestre}
                  onChange={(e) => setSemestre(e.target.value)}
                >
                  <option value="1">1</option>
                  <option value="2">2</option>
                </select>
              </div>

              <div className="campo">
                <label htmlFor="edicion-inicio">Fecha de inicio</label>
                <input
                  id="edicion-inicio"
                  type="date"
                  value={fechaInicio}
                  onChange={(e) => setFechaInicio(e.target.value)}
                />
              </div>

              <div className="campo">
                <label htmlFor="edicion-fin">Fecha de fin</label>
                <input
                  id="edicion-fin"
                  type="date"
                  value={fechaFin}
                  onChange={(e) => setFechaFin(e.target.value)}
                />
              </div>
            </div>

            <div className="modal-acciones">
              <button type="submit" className="btn btn-primario">Crear edición</button>
            </div>
          </form>

          {mensajeForm && <p className={errorForm ? "error" : "aviso"}>{mensajeForm}</p>}
        </div>
      )}
    </section>
  );
}