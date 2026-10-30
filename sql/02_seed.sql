-- =====================================================================
-- Torneo Interfacultades de Fútbol 5 – UCU
-- Datos maestros y de prueba (se ejecuta después de 01_schema.sql)
--
-- Estado del torneo de prueba (edición 2026 / semestre 2, en curso):
--   * 6 equipos, 5 a 10 jugadores por plantel, máx. 2 docentes/funcionarios
--   * Fechas 1 a 4 disputadas, fecha 5 programada, fecha 6 = reprogramación
--   * Incluye un partido cancelado (id 6) y uno postergado (id 9)
--   * Sanciones por roja, por acumulación de amarillas y disciplinaria
--   * Autogoles, jugadores sin equipo y jugadores que nunca figuraron en planilla
-- =====================================================================

USE torneo_db;

-- ---------------------------------------------------------------------
-- Usuarios de la aplicación (contraseñas hasheadas con bcrypt)
--   admin@ucu.edu.uy      / Admin2026!       (administrador)
--   planillero@ucu.edu.uy / Planillero2026!  (planillero)
-- ---------------------------------------------------------------------

SET NAMES utf8mb4;
INSERT INTO login (correo, contrasena, rol) VALUES
  ('admin@ucu.edu.uy', '$2b$12$/7.K5OLde4JO4niPPFEzIeqHDrc0TBvN0Lx7CvkmTM7Z7AOJ.o.Fi', 'administrador'),
  ('planillero@ucu.edu.uy', '$2b$12$cdL8lu7f6ngHmMCdc3mWz.dpqERS.wBtBqSDWcZiPFyAY2/0.W05u', 'planillero');

-- Facultades
INSERT INTO facultad (id_facultad, nombre) VALUES
  (1, 'Ingeniería y Tecnologías'),
  (2, 'Ciencias Empresariales'),
  (3, 'Derecho'),
  (4, 'Psicología'),
  (5, 'Ciencias de la Salud'),
  (6, 'Ciencias Humanas');

-- Turnos (1 hora, de 18:00 a 23:00)
INSERT INTO turno (id_turno, hora_inicio, hora_fin) VALUES
  (1, '18:00:00', '19:00:00'),
  (2, '19:00:00', '20:00:00'),
  (3, '20:00:00', '21:00:00'),
  (4, '21:00:00', '22:00:00'),
  (5, '22:00:00', '23:00:00');

-- Complejos y canchas
INSERT INTO complejo (id_complejo, nombre, direccion, departamento) VALUES
  (1, 'Complejo Deportivo Campus UCU', 'Av. 8 de Octubre 2738', 'Montevideo'),
  (2, 'Fútbol 5 Carrasco', 'Av. Italia 5832', 'Montevideo'),
  (3, 'Canchas del Este', 'Ruta Interbalnearia km 30', 'Canelones');

INSERT INTO cancha (nombre_cancha, id_complejo, superficie, techada) VALUES
  ('Cancha 1', 1, 'sintetico', FALSE),
  ('Cancha 2', 1, 'parquet', TRUE),
  ('Cancha A', 2, 'sintetico', TRUE),
  ('Cancha B', 2, 'sintetico', FALSE),
  ('Cancha Norte', 3, 'sintetico', FALSE);

-- Torneo
INSERT INTO torneo (id_torneo, nombre, anio, semestre, fecha_inicio, fecha_fin, estado) VALUES
  (1, 'Torneo Interfacultades de Fútbol 5 – 2026 S2', 2026, 2, '2026-09-28', '2026-11-24', 'en curso');

-- Jugadores (incluye 4 que no integran ningún equipo)
INSERT INTO jugador (ci, nombre, apellido, email, fecha_nacimiento, id_facultad, tipo) VALUES
  ('44353607', 'Andrés', 'Giménez', 'andres.gimenez@correo.ucu.edu.uy', '2003-11-20', 1, 'grado'),
  ('16316518', 'Cecilia', 'Álvarez', 'cecilia.alvarez@correo.ucu.edu.uy', '2003-05-05', 1, 'grado'),
  ('56535868', 'Agustín', 'Viera', 'agustin.viera@correo.ucu.edu.uy', '2005-01-20', 1, 'grado'),
  ('53883998', 'Valentina', 'Vázquez', 'valentina.vazquez@correo.ucu.edu.uy', '2005-10-21', 1, 'grado'),
  ('11006682', 'Diego', 'Píriz', 'diego.piriz@correo.ucu.edu.uy', '2004-02-02', 1, 'grado'),
  ('26236520', 'Matías', 'Romero', 'matias.romero@correo.ucu.edu.uy', '2004-01-25', 1, 'grado'),
  ('39563542', 'Agustina', 'Castro', 'agustina.castro@correo.ucu.edu.uy', '1999-04-17', 1, 'posgrado'),
  ('29740177', 'Mateo', 'Zunino', 'mateo.zunino@ucu.edu.uy', '1980-01-22', 1, 'docente'),
  ('53942994', 'Agustín', 'Gutiérrez', 'agustin.gutierrez@ucu.edu.uy', '1978-07-18', 1, 'funcionario'),
  ('47791837', 'Santiago', 'Martínez', 'santiago.martinez@correo.ucu.edu.uy', '2000-07-04', 2, 'grado'),
  ('35938484', 'Mariana', 'Pereira', 'mariana.pereira@correo.ucu.edu.uy', '2000-01-28', 2, 'grado'),
  ('24327855', 'Ricardo', 'González', 'ricardo.gonzalez@correo.ucu.edu.uy', '2001-01-16', 2, 'grado'),
  ('36670699', 'Camila', 'Peralta', 'camila.peralta@correo.ucu.edu.uy', '2003-02-19', 2, 'grado'),
  ('55292387', 'Juan', 'Romero', 'juan.romero@correo.ucu.edu.uy', '2002-06-03', 2, 'grado'),
  ('11016666', 'Ignacio', 'Ferreira', 'ignacio.ferreira@correo.ucu.edu.uy', '1996-02-05', 2, 'posgrado'),
  ('16781103', 'Franco', 'Peralta', 'franco.peralta@correo.ucu.edu.uy', '1990-01-15', 2, 'posgrado'),
  ('21923777', 'Verónica', 'Ortiz', 'veronica.ortiz@ucu.edu.uy', '1982-04-15', 2, 'docente'),
  ('38236431', 'Federico', 'Olivera', 'federico.olivera@correo.ucu.edu.uy', '2001-01-09', 3, 'grado'),
  ('49778150', 'Silvana', 'Giménez', 'silvana.gimenez@correo.ucu.edu.uy', '2002-01-07', 3, 'grado'),
  ('50400777', 'Andrés', 'Olivera', 'andres.olivera@correo.ucu.edu.uy', '2005-10-04', 3, 'grado'),
  ('24310520', 'Matías', 'Díaz', 'matias.diaz@correo.ucu.edu.uy', '2003-05-01', 3, 'grado'),
  ('32075824', 'Mauricio', 'Píriz', 'mauricio.piriz@correo.ucu.edu.uy', '2002-07-03', 3, 'grado'),
  ('24007855', 'Facundo', 'García', 'facundo.garcia@correo.ucu.edu.uy', '2004-11-08', 3, 'grado'),
  ('34741374', 'Martín', 'Bentancor', 'martin.bentancor@correo.ucu.edu.uy', '1995-10-15', 3, 'posgrado'),
  ('42462203', 'Gonzalo', 'Cáceres', 'gonzalo.caceres@ucu.edu.uy', '1988-03-28', 3, 'funcionario'),
  ('20635124', 'Alejandro', 'Romero', 'alejandro.romero@correo.ucu.edu.uy', '2005-11-18', 4, 'grado'),
  ('36052327', 'Lucas', 'Rossi', 'lucas.rossi@correo.ucu.edu.uy', '2003-10-03', 4, 'grado'),
  ('16968563', 'Lucía', 'López', 'lucia.lopez@correo.ucu.edu.uy', '2000-01-17', 4, 'grado'),
  ('59649060', 'Rodrigo', 'Rivero', 'rodrigo.rivero@correo.ucu.edu.uy', '2005-07-09', 4, 'grado'),
  ('50028176', 'Lucía', 'Larrosa', 'lucia.larrosa@correo.ucu.edu.uy', '2003-05-17', 4, 'grado'),
  ('14615487', 'Andrés', 'Delgado', 'andres.delgado@correo.ucu.edu.uy', '1992-04-16', 4, 'posgrado'),
  ('51330373', 'Micaela', 'Ferrari', 'micaela.ferrari@ucu.edu.uy', '1984-02-09', 4, 'docente'),
  ('23688790', 'Bruno', 'Echeverría', 'bruno.echeverria@ucu.edu.uy', '1970-02-09', 4, 'funcionario'),
  ('48397639', 'Álvaro', 'Maidana', 'alvaro.maidana@correo.ucu.edu.uy', '2001-02-12', 5, 'grado'),
  ('40222191', 'Gonzalo', 'Amaral', 'gonzalo.amaral@correo.ucu.edu.uy', '2002-11-24', 5, 'grado'),
  ('49221122', 'Héctor', 'Maidana', 'hector.maidana@correo.ucu.edu.uy', '2001-10-02', 5, 'grado'),
  ('41862811', 'Ximena', 'Rodríguez', 'ximena.rodriguez@correo.ucu.edu.uy', '2002-12-10', 5, 'grado'),
  ('50156112', 'Matías', 'Rodríguez', 'matias.rodriguez@correo.ucu.edu.uy', '2005-02-16', 5, 'grado'),
  ('30875088', 'Facundo', 'Delgado', 'facundo.delgado@correo.ucu.edu.uy', '1995-03-03', 5, 'posgrado'),
  ('46647839', 'Facundo', 'Vázquez', 'facundo.vazquez@ucu.edu.uy', '1976-12-02', 5, 'docente'),
  ('15212298', 'Ricardo', 'Pintos', 'ricardo.pintos@correo.ucu.edu.uy', '2003-01-28', 6, 'grado'),
  ('10975261', 'Carolina', 'Rocha', 'carolina.rocha@correo.ucu.edu.uy', '2004-11-13', 6, 'grado'),
  ('10835315', 'Camila', 'Cáceres', 'camila.caceres@correo.ucu.edu.uy', '2004-02-03', 6, 'grado'),
  ('17756465', 'Agustín', 'Zunino', 'agustin.zunino@correo.ucu.edu.uy', '2002-07-24', 6, 'grado'),
  ('59327575', 'Pablo', 'Techera', 'pablo.techera@correo.ucu.edu.uy', '2005-10-15', 6, 'grado'),
  ('46322795', 'Florencia', 'Gutiérrez', 'florencia.gutierrez@correo.ucu.edu.uy', '2000-09-25', 6, 'grado'),
  ('30819517', 'Paula', 'Rodríguez', 'paula.rodriguez@correo.ucu.edu.uy', '1999-02-16', 6, 'posgrado'),
  ('56864447', 'Santiago', 'Benítez', 'santiago.benitez@correo.ucu.edu.uy', '1991-08-25', 6, 'posgrado'),
  ('42634859', 'Fernanda', 'Lemes', 'fernanda.lemes@correo.ucu.edu.uy', '2002-01-12', 1, 'grado'),
  ('55509002', 'Ignacio', 'Díaz', 'ignacio.diaz@correo.ucu.edu.uy', '2004-04-17', 2, 'grado'),
  ('32986414', 'Diego', 'Alonso', 'diego.alonso@correo.ucu.edu.uy', '1997-08-08', 3, 'posgrado'),
  ('54687729', 'Tomás', 'Olivera', 'tomas.olivera@correo.ucu.edu.uy', '2002-04-21', 6, 'grado');

-- Equipos (el capitán es uno de sus jugadores)
INSERT INTO equipo (id_equipo, nombre, id_torneo, id_facultad, ci_capitan) VALUES
  (1, 'Ingeniería FC', 1, 1, '44353607'),
  (2, 'Empresariales United', 1, 2, '47791837'),
  (3, 'Derecho Atlético', 1, 3, '38236431'),
  (4, 'Psicología Sport Club', 1, 4, '20635124'),
  (5, 'Salud Rovers', 1, 5, '48397639'),
  (6, 'Humanas Deportivo', 1, 6, '15212298');

-- Planteles
INSERT INTO equipo_jugador_torneo (id_equipo, ci_jugador, id_torneo, numero_camiseta) VALUES
  -- Ingeniería FC
  (1, '44353607', 1, 15),
  (1, '16316518', 1, 28),
  (1, '56535868', 1, 18),
  (1, '53883998', 1, 25),
  (1, '11006682', 1, 29),
  (1, '26236520', 1, 26),
  (1, '39563542', 1, 17),
  (1, '29740177', 1, 19),
  (1, '53942994', 1, 7),
  -- Empresariales United
  (2, '47791837', 1, 27),
  (2, '35938484', 1, 3),
  (2, '24327855', 1, 23),
  (2, '36670699', 1, 9),
  (2, '55292387', 1, 11),
  (2, '11016666', 1, 8),
  (2, '16781103', 1, 17),
  (2, '21923777', 1, 10),
  -- Derecho Atlético
  (3, '38236431', 1, 17),
  (3, '49778150', 1, 7),
  (3, '50400777', 1, 24),
  (3, '24310520', 1, 25),
  (3, '32075824', 1, 5),
  (3, '24007855', 1, 14),
  (3, '34741374', 1, 21),
  (3, '42462203', 1, 13),
  -- Psicología Sport Club
  (4, '20635124', 1, 13),
  (4, '36052327', 1, 6),
  (4, '16968563', 1, 21),
  (4, '59649060', 1, 5),
  (4, '50028176', 1, 10),
  (4, '14615487', 1, 8),
  (4, '51330373', 1, 20),
  (4, '23688790', 1, 24),
  -- Salud Rovers
  (5, '48397639', 1, 14),
  (5, '40222191', 1, 15),
  (5, '49221122', 1, 8),
  (5, '41862811', 1, 2),
  (5, '50156112', 1, 26),
  (5, '30875088', 1, 6),
  (5, '46647839', 1, 10),
  -- Humanas Deportivo
  (6, '15212298', 1, 29),
  (6, '10975261', 1, 24),
  (6, '10835315', 1, 28),
  (6, '17756465', 1, 23),
  (6, '59327575', 1, 5),
  (6, '46322795', 1, 11),
  (6, '30819517', 1, 12),
  (6, '56864447', 1, 3);

-- Partidos
INSERT INTO partido (id_partido, id_torneo, numero_fecha, id_equipo_local, id_equipo_visitante, dia, id_turno, nombre_cancha, id_complejo, estado) VALUES
  -- Fecha 1: Ingeniería FC vs Humanas Deportivo (1-3)
  (1, 1, 1, 1, 6, '2026-09-29', 3, 'Cancha 1', 1, 'jugado'),
  -- Fecha 1: Empresariales United vs Salud Rovers (0-4)
  (2, 1, 1, 2, 5, '2026-09-29', 3, 'Cancha 2', 1, 'jugado'),
  -- Fecha 1: Derecho Atlético vs Psicología Sport Club (3-3)
  (3, 1, 1, 3, 4, '2026-09-29', 4, 'Cancha A', 2, 'jugado'),
  -- Fecha 2: Ingeniería FC vs Salud Rovers (0-5)
  (4, 1, 2, 1, 5, '2026-10-06', 3, 'Cancha 1', 1, 'jugado'),
  -- Fecha 2: Humanas Deportivo vs Psicología Sport Club (0-3)
  (5, 1, 2, 6, 4, '2026-10-06', 4, 'Cancha A', 2, 'jugado'),
  -- Fecha 2: Empresariales United vs Derecho Atlético (cancelado)
  (6, 1, 2, 2, 3, '2026-10-06', 3, 'Cancha 2', 1, 'cancelado'),
  -- Fecha 3: Ingeniería FC vs Psicología Sport Club (1-3)
  (7, 1, 3, 1, 4, '2026-10-13', 4, 'Cancha 1', 1, 'jugado'),
  -- Fecha 3: Salud Rovers vs Derecho Atlético (0-2)
  (8, 1, 3, 5, 3, '2026-10-13', 2, 'Cancha B', 2, 'jugado'),
  -- Fecha 3: Humanas Deportivo vs Empresariales United (postergado)
  (9, 1, 3, 6, 2, '2026-10-13', 3, 'Cancha Norte', 3, 'postergado'),
  -- Fecha 4: Ingeniería FC vs Derecho Atlético (3-2)
  (10, 1, 4, 1, 3, '2026-10-20', 3, 'Cancha 1', 1, 'jugado'),
  -- Fecha 4: Psicología Sport Club vs Empresariales United (4-2)
  (11, 1, 4, 4, 2, '2026-10-20', 4, 'Cancha A', 2, 'jugado'),
  -- Fecha 4: Salud Rovers vs Humanas Deportivo (4-3)
  (12, 1, 4, 5, 6, '2026-10-20', 2, 'Cancha 2', 1, 'jugado'),
  -- Fecha 5: Ingeniería FC vs Empresariales United (programado)
  (13, 1, 5, 1, 2, '2026-11-03', 3, 'Cancha 1', 1, 'programado'),
  -- Fecha 5: Derecho Atlético vs Humanas Deportivo (programado)
  (14, 1, 5, 3, 6, '2026-11-03', 3, 'Cancha A', 2, 'programado'),
  -- Fecha 5: Psicología Sport Club vs Salud Rovers (programado)
  (15, 1, 5, 4, 5, '2026-11-03', 4, 'Cancha 2', 1, 'programado'),
  -- Fecha 6: Empresariales United vs Derecho Atlético (programado)
  (16, 1, 6, 2, 3, '2026-11-10', 3, 'Cancha 1', 1, 'programado');

-- Planillas de juego (solo de partidos jugados)
INSERT INTO planilla_partido (id_partido, ci_jugador, id_equipo) VALUES
  (1, '53883998', 1),
  (1, '16316518', 1),
  (1, '29740177', 1),
  (1, '39563542', 1),
  (1, '56535868', 1),
  (1, '44353607', 1),
  (1, '26236520', 1),
  (1, '17756465', 6),
  (1, '10835315', 6),
  (1, '15212298', 6),
  (1, '59327575', 6),
  (1, '10975261', 6),
  (1, '30819517', 6),
  (2, '16781103', 2),
  (2, '47791837', 2),
  (2, '11016666', 2),
  (2, '36670699', 2),
  (2, '55292387', 2),
  (2, '35938484', 2),
  (2, '40222191', 5),
  (2, '30875088', 5),
  (2, '50156112', 5),
  (2, '41862811', 5),
  (2, '49221122', 5),
  (2, '48397639', 5),
  (3, '24310520', 3),
  (3, '50400777', 3),
  (3, '49778150', 3),
  (3, '38236431', 3),
  (3, '24007855', 3),
  (3, '42462203', 3),
  (3, '32075824', 3),
  (3, '59649060', 4),
  (3, '20635124', 4),
  (3, '16968563', 4),
  (3, '50028176', 4),
  (3, '36052327', 4),
  (3, '14615487', 4),
  (4, '56535868', 1),
  (4, '39563542', 1),
  (4, '11006682', 1),
  (4, '16316518', 1),
  (4, '26236520', 1),
  (4, '44353607', 1),
  (4, '29740177', 1),
  (4, '40222191', 5),
  (4, '41862811', 5),
  (4, '48397639', 5),
  (4, '49221122', 5),
  (4, '50156112', 5),
  (4, '30875088', 5),
  (5, '10835315', 6),
  (5, '46322795', 6),
  (5, '30819517', 6),
  (5, '10975261', 6),
  (5, '59327575', 6),
  (5, '17756465', 6),
  (5, '15212298', 6),
  (5, '14615487', 4),
  (5, '50028176', 4),
  (5, '20635124', 4),
  (5, '16968563', 4),
  (5, '59649060', 4),
  (5, '51330373', 4),
  (5, '36052327', 4),
  (7, '56535868', 1),
  (7, '26236520', 1),
  (7, '44353607', 1),
  (7, '29740177', 1),
  (7, '53883998', 1),
  (7, '39563542', 1),
  (7, '50028176', 4),
  (7, '14615487', 4),
  (7, '36052327', 4),
  (7, '20635124', 4),
  (7, '51330373', 4),
  (7, '59649060', 4),
  (8, '40222191', 5),
  (8, '30875088', 5),
  (8, '41862811', 5),
  (8, '48397639', 5),
  (8, '50156112', 5),
  (8, '49221122', 5),
  (8, '24310520', 3),
  (8, '32075824', 3),
  (8, '50400777', 3),
  (8, '42462203', 3),
  (8, '38236431', 3),
  (8, '49778150', 3),
  (8, '24007855', 3),
  (10, '56535868', 1),
  (10, '39563542', 1),
  (10, '53883998', 1),
  (10, '16316518', 1),
  (10, '29740177', 1),
  (10, '26236520', 1),
  (10, '42462203', 3),
  (10, '24310520', 3),
  (10, '49778150', 3),
  (10, '24007855', 3),
  (10, '38236431', 3),
  (10, '50400777', 3),
  (10, '32075824', 3),
  (11, '59649060', 4),
  (11, '51330373', 4),
  (11, '50028176', 4),
  (11, '14615487', 4),
  (11, '20635124', 4),
  (11, '36052327', 4),
  (11, '35938484', 2),
  (11, '55292387', 2),
  (11, '16781103', 2),
  (11, '47791837', 2),
  (11, '36670699', 2),
  (11, '11016666', 2),
  (12, '41862811', 5),
  (12, '49221122', 5),
  (12, '48397639', 5),
  (12, '30875088', 5),
  (12, '50156112', 5),
  (12, '30819517', 6),
  (12, '10975261', 6),
  (12, '59327575', 6),
  (12, '15212298', 6),
  (12, '17756465', 6),
  (12, '46322795', 6);

-- Goles (autogol = 1: suma para el equipo rival al del jugador)
INSERT INTO gol (id_partido, ci_jugador, minuto, autogol) VALUES
  (1, '10975261', 21, 0),
  (1, '15212298', 25, 0),
  (1, '26236520', 29, 0),
  (1, '17756465', 40, 0),
  (2, '48397639', 11, 0),
  (2, '41862811', 18, 0),
  (2, '48397639', 34, 0),
  (2, '40222191', 35, 0),
  (3, '14615487', 22, 0),
  (3, '16968563', 31, 0),
  (3, '49778150', 33, 0),
  (3, '50400777', 36, 0),
  (3, '24007855', 52, 1),
  (3, '59649060', 59, 1),
  (4, '48397639', 3, 0),
  (4, '40222191', 6, 0),
  (4, '30875088', 35, 0),
  (4, '40222191', 52, 0),
  (4, '41862811', 52, 0),
  (5, '36052327', 11, 0),
  (5, '16968563', 35, 0),
  (5, '16968563', 41, 0),
  (7, '20635124', 8, 0),
  (7, '44353607', 13, 0),
  (7, '20635124', 13, 0),
  (7, '20635124', 22, 0),
  (8, '50400777', 12, 0),
  (8, '32075824', 24, 0),
  (10, '26236520', 4, 0),
  (10, '24007855', 12, 0),
  (10, '56535868', 20, 0),
  (10, '24007855', 22, 0),
  (10, '26236520', 23, 0),
  (11, '20635124', 11, 0),
  (11, '50028176', 20, 0),
  (11, '14615487', 27, 0),
  (11, '47791837', 36, 0),
  (11, '36052327', 39, 0),
  (11, '35938484', 48, 0),
  (12, '41862811', 8, 0),
  (12, '48397639', 9, 0),
  (12, '15212298', 9, 0),
  (12, '15212298', 16, 0),
  (12, '48397639', 17, 0),
  (12, '49221122', 34, 0),
  (12, '17756465', 50, 0);

-- Tarjetas
INSERT INTO tarjeta (id_partido, ci_jugador, minuto, color) VALUES
  (1, '53883998', 3, 'roja'),
  (2, '40222191', 13, 'amarilla'),
  (2, '47791837', 60, 'amarilla'),
  (3, '32075824', 15, 'amarilla'),
  (4, '50156112', 10, 'amarilla'),
  (4, '41862811', 17, 'amarilla'),
  (4, '29740177', 27, 'amarilla'),
  (4, '39563542', 28, 'amarilla'),
  (4, '40222191', 40, 'amarilla'),
  (4, '48397639', 50, 'amarilla'),
  (7, '59649060', 4, 'amarilla'),
  (7, '56535868', 49, 'amarilla'),
  (8, '40222191', 11, 'amarilla'),
  (8, '30875088', 51, 'amarilla'),
  (8, '48397639', 54, 'amarilla'),
  (8, '41862811', 58, 'amarilla'),
  (10, '38236431', 13, 'amarilla'),
  (10, '24310520', 16, 'amarilla'),
  (10, '42462203', 40, 'amarilla'),
  (10, '32075824', 17, 'roja'),
  (11, '51330373', 11, 'amarilla'),
  (11, '20635124', 21, 'amarilla'),
  (11, '35938484', 4, 'roja');

-- Sanciones (la suspensión se cumple desde numero_fecha_inicio durante cantidad_fechas)
INSERT INTO sancion_jugador (ci_jugador, id_torneo, motivo, numero_fecha_inicio, cantidad_fechas) VALUES
  ('16968563', 1, 'disciplinaria', 3, 2),
  ('53883998', 1, 'roja', 2, 1),
  ('40222191', 1, 'acumulacion_amarillas', 4, 1),
  ('32075824', 1, 'roja', 5, 1),
  ('35938484', 1, 'roja', 5, 1);