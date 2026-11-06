import {
  jugadoresPorFacultad,
  porcentajePorEstados,
  cantidadSanciones,
  canchasUsadas,
  turnosUsados,
  topJugadores,
  jugadoresNoPlanilla,
  fairPlay,
  promedioGolesPartidoFecha,
  promedioGolesPartidoEdicion,
  tablaPosiciones,
  edadPromedioPlantel,
  partidosJugadosPorComplejo,
  golesPorFacultad
} from "../api/reportes";

import ReportePorEdicion from "../components/ReportePorEdicion";
import ReporteTabla from "../components/ReporteTabla";

const columnasJugadoresPorFacultad = [
  { key: "nombre_facultad", label: "Facultad" },
  { key: "tipo_jugador", label: "Tipo de jugador" },
  { key: "cantidad_jugador", label: "Cantidad de jugadores" },
];

const columnasPartidosPorEstado = [
  { key: "estado", label: "Estado" },
  { key: "cantidad", label: "Partidos" },
  { key: "porcentaje", label: "Porcentaje (%)" },
];

const columnasSanciones = [
  { key: "equipo", label: "Equipo" },
  { key: "motivo", label: "Motivo" },
  { key: "cantidad_sanciones", label: "Sanciones" },
];

const columnasCanchas = [
  { key: "complejo_nombre", label: "Complejo" },
  { key: "nombre_cancha", label: "Cancha" },
  { key: "cantidad_usos", label: "Partidos" },
];

const columnasTurnos = [
  { key: "hora_inicio", label: "Desde" },
  { key: "hora_fin", label: "Hasta" },
  { key: "turno_mas_utilizados", label: "Partidos" },
];

const columnasGoleadores = [
  { key: "nombre", label: "Nombre" },
  { key: "apellido", label: "Apellido" },
  { key: "cantidad_goles", label: "Goles" },
];

const columnasSinPartidos = [
  { key: "jugador_nombre", label: "Nombre" },
  { key: "jugador_apellido", label: "Apellido" },
  { key: "equipo_nombre", label: "Equipo" },
];

const columnasFairPlay = [
  { key: "equipo", label: "Equipo" },
  { key: "amarillas", label: "Amarillas" },
  { key: "rojas", label: "Rojas" },
  { key: "puntos", label: "Puntos" },
];

const columnasPromedioPorFecha = [
  { key: "numero_fecha", label: "Fecha" },
  { key: "partidos_jugados", label: "Partidos jugados" },
  { key: "goles", label: "Goles" },
  { key: "promedio_goles", label: "Promedio de goles" },
];

const columnasPromedioEdicion = [
  { key: "partidos_jugados", label: "Partidos jugados" },
  { key: "goles", label: "Goles" },
  { key: "promedio_goles", label: "Promedio de goles" },
];


const columnasPosiciones = [
  { key: "equipo", label: "Equipo" },
  { key: "PJ", label: "PJ" },
  { key: "PG", label: "PG" },
  { key: "PE", label: "PE" },
  { key: "PP", label: "PP" },
  { key: "GF", label: "GF" },
  { key: "GC", label: "GC" },
  { key: "DG", label: "DG" },
  { key: "Pts", label: "Pts" },
];



export default function Reportes() {
  return (
    <div>
        <h2>Reportes</h2>
        <ReporteTabla titulo="Jugadores por facultad y tipo" pedirDatos={jugadoresPorFacultad} columnas={columnasJugadoresPorFacultad} />
        <ReporteTabla titulo="Partidos jugados vs. postergados y cancelados" pedirDatos={porcentajePorEstados} columnas={columnasPartidosPorEstado} />
        <ReporteTabla titulo="Sanciones por equipo y motivo" pedirDatos={cantidadSanciones} columnas={columnasSanciones} />
        <ReporteTabla titulo="Canchas más utilizadas" pedirDatos={canchasUsadas} columnas={columnasCanchas} />
        <ReporteTabla titulo="Turnos más utilizados" pedirDatos={turnosUsados} columnas={columnasTurnos} />
        <ReporteTabla titulo="Goleadores (top 10)" pedirDatos={topJugadores} columnas={columnasGoleadores} />
        <ReporteTabla titulo="Inscriptos que nunca figuraron en una planilla" pedirDatos={jugadoresNoPlanilla} columnas={columnasSinPartidos} />
        <ReporteTabla titulo="Fair play por equipo" pedirDatos={fairPlay} columnas={columnasFairPlay} />
        <ReportePorEdicion titulo="Promedio de goles por partido, por fecha" pedirDatos={promedioGolesPartidoFecha} columnas={columnasPromedioPorFecha} />
        <ReportePorEdicion titulo="Promedio de goles por partido en la edición" pedirDatos={promedioGolesPartidoEdicion} columnas={columnasPromedioEdicion} />  
        <ReportePorEdicion titulo="Tabla de posiciones" pedirDatos={tablaPosiciones} columnas={columnasPosiciones} />
        <ReportePorEdicion titulo="Edad promedio del plantel" pedirDatos={edadPromedioPlantel} columnas={[{ key: "equipo", label: "Equipo" }, { key: "edad_promedio", label: "Edad promedio" }]} />
        <ReportePorEdicion titulo="Partidos jugados por complejo" pedirDatos={partidosJugadosPorComplejo} columnas={[{ key: "complejo", label: "Complejo" }, { key: "partidos_jugados", label: "Partidos jugados" }]} />
        <ReportePorEdicion titulo="Goles por facultad" pedirDatos={golesPorFacultad} columnas={[{ key: "facultad", label: "Facultad" }, { key: "goles", label: "Goles" }]} />
    </div>
        
  );
}