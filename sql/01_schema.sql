-- =====================================================================
-- Torneo Interfacultades de Fútbol 5 – UCU
-- Script de creación de la base de datos
-- =====================================================================

SET NAMES utf8mb4;
DROP DATABASE IF EXISTS torneo_db;
CREATE DATABASE torneo_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE torneo_db;

-- ---------------------------------------------------------------------
-- 1. Tablas sin claves foráneas
-- ---------------------------------------------------------------------

CREATE TABLE facultad (
  id_facultad INT AUTO_INCREMENT PRIMARY KEY,
  nombre      VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE login (
  correo     VARCHAR(100) PRIMARY KEY,
  contrasena VARCHAR(255) NOT NULL,              -- se guarda el hash, nunca la contraseña
  rol        ENUM('administrador', 'planillero') NOT NULL,
  CONSTRAINT chk_login_correo CHECK (correo LIKE '%_@_%._%') -- verifica los caracteres del mail
);

CREATE TABLE complejo (
  id_complejo  INT AUTO_INCREMENT PRIMARY KEY,
  nombre       VARCHAR(100) NOT NULL UNIQUE,
  direccion    VARCHAR(150) NOT NULL,
  departamento VARCHAR(50)  NOT NULL
);

CREATE TABLE turno (
  id_turno    INT AUTO_INCREMENT PRIMARY KEY,
  hora_inicio TIME NOT NULL UNIQUE,
  hora_fin    TIME NOT NULL,
  CONSTRAINT chk_turno_orden  CHECK (hora_fin > hora_inicio),
  CONSTRAINT chk_turno_franja CHECK (hora_inicio >= '18:00:00' AND hora_fin <= '23:00:00')
);

-- ---------------------------------------------------------------------
-- 2. Tablas que dependen de las anteriores
-- ---------------------------------------------------------------------

CREATE TABLE jugador (
  ci               VARCHAR(8)   PRIMARY KEY,
  nombre           VARCHAR(50)  NOT NULL,
  apellido         VARCHAR(50)  NOT NULL,
  email            VARCHAR(100) NOT NULL UNIQUE,
  fecha_nacimiento DATE         NOT NULL,        -- "anterior a hoy" se valida en Python
  id_facultad      INT          NOT NULL,
  tipo ENUM('grado', 'posgrado', 'docente', 'funcionario') NOT NULL,
  CONSTRAINT fk_jugador_facultad FOREIGN KEY (id_facultad) REFERENCES facultad (id_facultad),
  CONSTRAINT chk_jugador_ci      CHECK (ci REGEXP '^[0-9]{7,8}$'), -- sacar lo puntos y guiones con funcion normalizadora
  CONSTRAINT chk_jugador_email   CHECK (email LIKE '%_@_%._%') -- controla que tenga formato email
);

CREATE TABLE torneo (
  id_torneo    INT AUTO_INCREMENT PRIMARY KEY,
  nombre       VARCHAR(100) NOT NULL,
  anio         SMALLINT     NOT NULL,
  semestre     TINYINT      NOT NULL,
  fecha_inicio DATE         NOT NULL,
  fecha_fin    DATE         NOT NULL,
  estado ENUM('inscripcion', 'en curso', 'finalizado') NOT NULL DEFAULT 'inscripcion',
  CONSTRAINT uq_torneo_edicion UNIQUE (anio, semestre),   -- una edición por semestre
  CONSTRAINT chk_torneo_semestre CHECK (semestre IN (1, 2)),
  CONSTRAINT chk_torneo_anio     CHECK (anio BETWEEN 2000 AND 2100),
  CONSTRAINT chk_torneo_fechas   CHECK (fecha_fin > fecha_inicio)
);

CREATE TABLE cancha (
  nombre_cancha VARCHAR(50) NOT NULL,
  id_complejo   INT         NOT NULL,
  superficie    ENUM('sintetico', 'parquet') NOT NULL,
  techada       BOOLEAN     NOT NULL DEFAULT FALSE,
  PRIMARY KEY (nombre_cancha, id_complejo),
  CONSTRAINT fk_cancha_complejo FOREIGN KEY (id_complejo) REFERENCES complejo (id_complejo)
);

CREATE TABLE equipo (
  id_equipo   INT AUTO_INCREMENT PRIMARY KEY,
  nombre      VARCHAR(100) NOT NULL,
  id_torneo   INT          NOT NULL,
  id_facultad INT          NOT NULL,
  ci_capitan  VARCHAR(8)   NULL,     -- NULL al crear: se asigna después de cargar el plantel
  CONSTRAINT uq_equipo_nombre        UNIQUE (nombre, id_torneo),
  CONSTRAINT uq_equipo_torneo        UNIQUE (id_equipo, id_torneo),   -- lo usan las FK de abajo
  CONSTRAINT fk_equipo_torneo        FOREIGN KEY (id_torneo)   REFERENCES torneo (id_torneo),
  CONSTRAINT fk_equipo_facultad      FOREIGN KEY (id_facultad) REFERENCES facultad (id_facultad),
  CONSTRAINT fk_equipo_capitan       FOREIGN KEY (ci_capitan)  REFERENCES jugador (ci)
);

-- ---------------------------------------------------------------------
-- 3. Plantel y partidos
-- ---------------------------------------------------------------------

CREATE TABLE equipo_jugador_torneo (
  id_equipo       INT        NOT NULL,
  ci_jugador      VARCHAR(8) NOT NULL,
  id_torneo       INT        NOT NULL,
  numero_camiseta TINYINT    NOT NULL,
  PRIMARY KEY (id_equipo, ci_jugador),
  CONSTRAINT uq_plantel_jugador_torneo UNIQUE (ci_jugador, id_torneo),     -- un equipo por edición
  CONSTRAINT uq_plantel_camiseta       UNIQUE (id_equipo, numero_camiseta),
  -- garantiza que id_torneo coincida con el torneo del equipo
  CONSTRAINT fk_plantel_equipo  FOREIGN KEY (id_equipo, id_torneo) REFERENCES equipo (id_equipo, id_torneo),
  CONSTRAINT fk_plantel_jugador FOREIGN KEY (ci_jugador) REFERENCES jugador (ci),
  CONSTRAINT chk_plantel_camiseta CHECK (numero_camiseta BETWEEN 1 AND 99)
);

CREATE TABLE partido (
  id_partido          INT AUTO_INCREMENT PRIMARY KEY,
  id_torneo           INT         NOT NULL,
  numero_fecha        TINYINT     NOT NULL,
  id_equipo_local     INT         NOT NULL,
  id_equipo_visitante INT         NOT NULL,
  dia                 DATE        NOT NULL,
  id_turno            INT         NOT NULL,
  nombre_cancha       VARCHAR(50) NOT NULL,
  id_complejo         INT         NOT NULL,
  estado ENUM('programado', 'jugado', 'postergado', 'cancelado') NOT NULL DEFAULT 'programado',
  -- una cancha no puede tener dos partidos el mismo día y turno
  CONSTRAINT uq_partido_cancha_turno UNIQUE (dia, id_turno, nombre_cancha, id_complejo),
  CONSTRAINT fk_partido_torneo    FOREIGN KEY (id_torneo) REFERENCES torneo (id_torneo),
  -- ambos equipos deben ser de la misma edición que el partido
  CONSTRAINT fk_partido_local     FOREIGN KEY (id_equipo_local, id_torneo)     REFERENCES equipo (id_equipo, id_torneo),
  CONSTRAINT fk_partido_visitante FOREIGN KEY (id_equipo_visitante, id_torneo) REFERENCES equipo (id_equipo, id_torneo),
  CONSTRAINT fk_partido_turno     FOREIGN KEY (id_turno) REFERENCES turno (id_turno),
  CONSTRAINT fk_partido_cancha    FOREIGN KEY (nombre_cancha, id_complejo) REFERENCES cancha (nombre_cancha, id_complejo),
  CONSTRAINT chk_partido_rivales  CHECK (id_equipo_local <> id_equipo_visitante),
  CONSTRAINT chk_partido_fecha    CHECK (numero_fecha >= 1)
);

-- ---------------------------------------------------------------------
-- 4. Lo que se registra en cada partido
-- ---------------------------------------------------------------------

CREATE TABLE planilla_partido (
  id_partido INT        NOT NULL,
  ci_jugador VARCHAR(8) NOT NULL,
  id_equipo  INT        NOT NULL,
  PRIMARY KEY (id_partido, ci_jugador),
  CONSTRAINT fk_planilla_partido FOREIGN KEY (id_partido) REFERENCES partido (id_partido),
  CONSTRAINT fk_planilla_plantel FOREIGN KEY (id_equipo, ci_jugador) REFERENCES equipo_jugador_torneo (id_equipo, ci_jugador)
);

CREATE TABLE gol (
  id_gol     INT AUTO_INCREMENT PRIMARY KEY,
  id_partido INT        NOT NULL,
  ci_jugador VARCHAR(8) NOT NULL,
  minuto     TINYINT    NOT NULL,
  autogol    BOOLEAN    NOT NULL DEFAULT FALSE,
  -- solo puede convertir quien figura en la planilla de ese partido
  CONSTRAINT fk_gol_planilla FOREIGN KEY (id_partido, ci_jugador) REFERENCES planilla_partido (id_partido, ci_jugador),
  CONSTRAINT chk_gol_minuto  CHECK (minuto BETWEEN 0 AND 60)
);

CREATE TABLE tarjeta (
  id_tarjeta INT AUTO_INCREMENT PRIMARY KEY,
  id_partido INT        NOT NULL,
  ci_jugador VARCHAR(8) NOT NULL,
  minuto     TINYINT    NOT NULL,
  color      ENUM('amarilla', 'roja') NOT NULL,
  -- solo puede recibir tarjeta quien figura en la planilla de ese partido
  CONSTRAINT fk_tarjeta_planilla FOREIGN KEY (id_partido, ci_jugador) REFERENCES planilla_partido (id_partido, ci_jugador),
  CONSTRAINT chk_tarjeta_minuto  CHECK (minuto BETWEEN 0 AND 60)
);

CREATE TABLE sancion_jugador (
  id_sancion          INT AUTO_INCREMENT PRIMARY KEY,
  ci_jugador          VARCHAR(8) NOT NULL,
  id_torneo           INT        NOT NULL,
  motivo ENUM('roja', 'acumulacion_amarillas', 'disciplinaria') NOT NULL,
  numero_fecha_inicio TINYINT    NOT NULL,
  cantidad_fechas     TINYINT    NOT NULL DEFAULT 1,
  CONSTRAINT fk_sancion_jugador FOREIGN KEY (ci_jugador) REFERENCES jugador (ci),
  CONSTRAINT fk_sancion_torneo  FOREIGN KEY (id_torneo)  REFERENCES torneo (id_torneo),
  CONSTRAINT chk_sancion_inicio   CHECK (numero_fecha_inicio >= 1),
  CONSTRAINT chk_sancion_cantidad CHECK (cantidad_fechas >= 1)
);

-- ---------------------------------------------------------------------
-- 5. Usuarios de la aplicación con permisos diferenciados
-- ---------------------------------------------------------------------

DROP USER IF EXISTS 'admin_app'@'%';
DROP USER IF EXISTS 'planillero_app'@'%';
DROP USER IF EXISTS 'login_app'@'%';

CREATE USER 'admin_app'@'%' IDENTIFIED BY 'Admin123!';
GRANT SELECT, INSERT, UPDATE, DELETE ON torneo_db.* TO 'admin_app'@'%';

-- El planillero lee todo, pero solo escribe la planilla, goles y tarjetas
-- (y crea sanciones, porque una roja o la 3.ª amarilla genera una automática)
CREATE USER 'planillero_app'@'%' IDENTIFIED BY 'Planilla123!';
GRANT SELECT ON torneo_db.* TO 'planillero_app'@'%';
GRANT INSERT, UPDATE, DELETE ON torneo_db.planilla_partido TO 'planillero_app'@'%';
GRANT INSERT, UPDATE, DELETE ON torneo_db.gol              TO 'planillero_app'@'%';
GRANT INSERT, UPDATE, DELETE ON torneo_db.tarjeta          TO 'planillero_app'@'%';
GRANT INSERT                 ON torneo_db.sancion_jugador  TO 'planillero_app'@'%';

-- Solo se usa para verificar correo y contraseña al iniciar sesión
CREATE USER 'login_app'@'%' IDENTIFIED BY 'Login123!';
GRANT SELECT ON torneo_db.login TO 'login_app'@'%';

FLUSH PRIVILEGES;