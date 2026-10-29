DROP DATABASE IF EXISTS torneo_db;
CREATE DATABASE torneo_db;
USE torneo_db;
CREATE TABLE prueba (id INT PRIMARY KEY, nombre VARCHAR(50));
INSERT INTO prueba VALUES (1, 'funciona');