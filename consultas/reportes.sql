-- =====================================================================
-- Consultas-Reportes
-- =====================================================================


-- =====================================================================
-- 1) Tabla de posiciones de una edición del torneo (partidos jugados,
--    ganados, empatados y perdidos, goles a favor, goles en contra,
--    diferencia de goles y puntos)
-- =====================================================================


SELECT equipo.nombre AS equipo,
       COUNT(*) AS PJ,
       SUM(CASE WHEN equipo.id_equipo = resultado.id_equipo_local
         THEN resultado.goles_local
         ELSE resultado.goles_visitante END) AS GF,
       SUM(CASE WHEN equipo.id_equipo = resultado.id_equipo_local
         THEN resultado.goles_visitante
         ELSE resultado.goles_local END) AS GC,
       SUM(CASE WHEN (equipo.id_equipo = resultado.id_equipo_local AND resultado.goles_local > resultado.goles_visitante)
         OR (equipo.id_equipo = resultado.id_equipo_visitante AND resultado.goles_visitante > resultado.goles_local)
         THEN 1 ELSE 0 END) AS PG,
       SUM(CASE WHEN resultado.goles_local = resultado.goles_visitante THEN 1 ELSE 0 END) AS PE,
       SUM(CASE WHEN (equipo.id_equipo = resultado.id_equipo_local AND resultado.goles_local < resultado.goles_visitante)
         OR (equipo.id_equipo = resultado.id_equipo_visitante AND resultado.goles_visitante < resultado.goles_local)
         THEN 1 ELSE 0 END) AS PP,
       SUM(CASE WHEN equipo.id_equipo = resultado.id_equipo_local
         THEN resultado.goles_local - resultado.goles_visitante
         ELSE resultado.goles_visitante - resultado.goles_local END) AS DG,
       SUM(CASE WHEN (equipo.id_equipo = resultado.id_equipo_local AND resultado.goles_local > resultado.goles_visitante)
         OR (equipo.id_equipo = resultado.id_equipo_visitante AND resultado.goles_visitante > resultado.goles_local)
         THEN 3
         WHEN resultado.goles_local = resultado.goles_visitante
         THEN 1
         ELSE 0 END) AS Pts
FROM equipo
JOIN (

    SELECT partido.id_partido, partido.id_equipo_local, partido.id_equipo_visitante,
       SUM(CASE WHEN (planilla_partido.id_equipo = partido.id_equipo_local AND gol.autogol = FALSE)
            OR (planilla_partido.id_equipo = partido.id_equipo_visitante AND gol.autogol = TRUE)
            THEN 1 ELSE 0 END) AS goles_local,
       SUM(CASE WHEN (planilla_partido.id_equipo = partido.id_equipo_visitante AND gol.autogol = FALSE)
            OR (planilla_partido.id_equipo = partido.id_equipo_local AND gol.autogol = TRUE)
            THEN 1 ELSE 0 END) AS goles_visitante
    from partido
    left join gol on partido.id_partido = gol.id_partido
    left join planilla_partido on gol.id_partido = planilla_partido.id_partido and gol.ci_jugador = planilla_partido.ci_jugador
    where id_torneo = 1 and estado = 'jugado'
    Group By partido.id_partido, partido.id_equipo_local, partido.id_equipo_visitante
    ) AS resultado
ON equipo.id_equipo = resultado.id_equipo_local
OR equipo.id_equipo = resultado.id_equipo_visitante
WHERE equipo.id_torneo = 1
GROUP BY equipo.id_equipo, equipo.nombre
ORDER BY Pts DESC, DG DESC, GF DESC;




-- =====================================================================
-- 2) Tabla de goleadores (los 10 jugadores con más goles)
-- =====================================================================

SELECT jugador.nombre, jugador.apellido, COUNT(*) as cantidad_goles
FROM gol
JOIN jugador on gol.ci_jugador = jugador.ci
WHERE gol.autogol = FALSE
GROUP BY gol.ci_jugador
ORDER BY cantidad_goles DESC
LIMIT 10;


-- =====================================================================
-- 3) Tabla de fair play por equipo (1 punto por cada tarjeta amarilla y 3 por cada
--    roja; el mejor equipo es el de menor puntaje)
-- =====================================================================

SELECT equipo.nombre AS equipo,
       SUM(CASE WHEN tarjeta.color = 'amarilla' THEN 1 ELSE 0 END) AS amarillas,
       SUM(CASE WHEN tarjeta.color = 'roja'     THEN 1 ELSE 0 END) AS rojas,
       SUM(CASE WHEN tarjeta.color = 'amarilla' THEN 1
                WHEN tarjeta.color = 'roja'     THEN 3
                ELSE 0 END) AS puntos
FROM equipo
LEFT JOIN planilla_partido
       ON planilla_partido.id_equipo = equipo.id_equipo
LEFT JOIN tarjeta
       ON tarjeta.id_partido = planilla_partido.id_partido
      AND tarjeta.ci_jugador = planilla_partido.ci_jugador
WHERE equipo.id_torneo = 1
GROUP BY equipo.id_equipo, equipo.nombre
ORDER BY puntos ASC, equipo.nombre;


-- =====================================================================
-- 4) Promedio de goles por partido en cada fecha y en toda la edición
-- =====================================================================

SELECT goles_partido.numero_fecha,
       COUNT(*) AS partidos_jugados,
       SUM(goles_partido.goles) AS goles,
       ROUND(AVG(goles_partido.goles), 2) AS promedio_goles
FROM (SELECT partido.id_partido, partido.numero_fecha, COUNT(gol.id_gol) AS goles
      FROM partido
      LEFT JOIN gol ON gol.id_partido = partido.id_partido
      WHERE partido.id_torneo = 1 AND partido.estado = 'jugado'
      GROUP BY partido.id_partido, partido.numero_fecha) AS goles_partido
GROUP BY goles_partido.numero_fecha
ORDER BY goles_partido.numero_fecha;


SELECT COUNT(*) AS partidos_jugados,
       SUM(goles_partido.goles) AS goles,
       ROUND(AVG(goles_partido.goles), 2) AS promedio_goles
FROM (SELECT partido.id_partido, COUNT(gol.id_gol) AS goles
      FROM partido
      LEFT JOIN gol ON gol.id_partido = partido.id_partido
      WHERE partido.id_torneo = 1 AND partido.estado = 'jugado'
      GROUP BY partido.id_partido) AS goles_partido;


-- =====================================================================
-- 5) Canchas y turnos más utilizados
-- =====================================================================

SELECT cancha.nombre_cancha, complejo.nombre as complejo_nombre, COUNT(*) as cantidad_usos
FROM partido
JOIN cancha on partido.nombre_cancha = cancha.nombre_cancha and partido.id_complejo = cancha.id_complejo
JOIN complejo on cancha.id_complejo = complejo.id_complejo
GROUP BY cancha.nombre_cancha, cancha.id_complejo
ORDER BY cantidad_usos DESC;


SELECT turno.id_turno, turno.hora_inicio, turno.hora_fin, COUNT(*) as turno_mas_utilizados
FROM partido
JOIN turno on partido.id_turno = turno.id_turno
GROUP BY turno.id_turno
ORDER BY turno_mas_utilizados DESC;



-- =====================================================================
-- 6) Cantidad de jugadores por facultad y por tipo (grado, posgrado,
--    docente, funcionario)
-- =====================================================================


SELECT COUNT(jugador.ci) as cantiad_jugador, facultad.nombre, jugador.tipo
FROM jugador
JOIN facultad on jugador.id_facultad = facultad.id_facultad
GROUP BY facultad.id_facultad, jugador.tipo;


-- =====================================================================
-- 7) Jugadores inscriptos en un plantel que nunca figuraron en
--    una planilla de juego
-- =====================================================================

SELECT jugador.nombre as jugador_nombre, jugador.apellido, equipo.nombre as equipo_nombre
from equipo_jugador_torneo
JOIN jugador on equipo_jugador_torneo.ci_jugador = jugador.ci
JOIN equipo on equipo_jugador_torneo.id_equipo = equipo.id_equipo and equipo_jugador_torneo.id_torneo = equipo.id_torneo
LEFT JOIN planilla_partido on equipo_jugador_torneo.ci_jugador = planilla_partido.ci_jugador
WHERE planilla_partido.ci_jugador IS NULL;


-- =====================================================================
-- 8) Cantidad de sanciones por equipo y por motivo
-- =====================================================================

SELECT equipo.nombre, sancion_jugador.motivo, COUNT(*) AS cantidad_sanciones
FROM sancion_jugador
JOIN equipo_jugador_torneo on sancion_jugador.ci_jugador = equipo_jugador_torneo.ci_jugador
JOIN equipo on equipo_jugador_torneo.id_equipo = equipo.id_equipo and equipo_jugador_torneo.id_torneo = equipo.id_torneo
GROUP BY equipo.nombre, sancion_jugador.motivo;



-- =====================================================================
-- 9) Porcentaje de partidos jugados vs. postergados/cancelados
-- =====================================================================

SELECT partido.estado, COUNT(*), ROUND(COUNT(*) / (SELECT COUNT(*) FROM partido) *100 , 1) AS porcentaje
FROM partido
GROUP BY partido.estado;


