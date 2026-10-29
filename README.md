# Torneo Interfacultades de Fútbol 5

Sistema de gestión del Torneo Interfacultades de Fútbol 5 (UCU). Este documento explica cómo levantar en local la **base de datos MySQL** y el **backend FastAPI** con Docker.

| Servicio | Tecnología | Puerto |
|---|---|---|
| `db` | MySQL 8.0 | `3306` |
| `backend` | FastAPI + PyMySQL | `8000` |

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) y Docker Compose v2 (`docker compose version` para verificarlo). En Windows, Docker Desktop debe estar abierto.
- Puertos `3306` y `8000` libres (ver [Problemas frecuentes](#problemas-frecuentes)).

## Estructura relevante

```
proyecto/
├── docker-compose.yml
├── .env                 # credenciales locales
├── .env.example         # plantilla de .env
├── sql/                 # scripts de inicialización de MySQL
│   ├── 01_schema.sql    # tablas, constraints, usuarios de MySQL y permisos por rol
│   └── 02_seed.sql      # datos maestros, usuarios de la app y datos de prueba
└── backend/
    ├── Dockerfile
    ├── requirements.txt
    └── app/             # código FastAPI (routers, schemas, repositories)
```

## Puesta en marcha

### 1. Crear el archivo `.env`

Linux / macOS / Git Bash:

```bash
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

Contenido de `.env.example`:

```env
MYSQL_ROOT_PASSWORD=cambiar_esta_password

# Usuarios de MySQL que crea sql/01_schema.sql.
# Las contraseñas deben coincidir con las de ese script.
DB_ADMIN_USER=admin_app
DB_ADMIN_PASSWORD=Admin123!
DB_PLANILLERO_USER=planillero_app
DB_PLANILLERO_PASSWORD=Planilla123!
DB_LOGIN_USER=login_app
DB_LOGIN_PASSWORD=Login123!
```

> `.env` debe estar en el `.gitignore`. Estas credenciales son solo para desarrollo local.

### 2. Levantar todo

```bash
docker compose up -d --build
```

La primera vez descarga `mysql:8.0`, construye la imagen del backend y ejecuta los scripts de `sql/`. El backend espera a que MySQL esté listo (healthcheck), así que puede tardar un minuto. Para seguir el progreso:

```bash
docker compose logs -f
```

Logs de un solo servicio: `docker compose logs -f db` o `docker compose logs -f backend`.

La base está lista cuando aparece `ready for connections`, y el backend cuando aparece `Application startup complete`.

### 3. Verificar que funciona

| Qué | URL / comando | Resultado esperado |
|---|---|---|
| Backend vivo | http://localhost:8000/health | `{"status":"ok"}` |
| Backend ↔ BD | http://localhost:8000/health/db | `{"db":true}` |
| Documentación de la API | http://localhost:8000/docs | Swagger UI |
| Tablas creadas | `docker compose exec db mysql -u root -p torneo_db -e "SHOW TABLES;"` | 14 tablas |

## Usuarios

### Usuarios de la aplicación (tabla `login`)

Se cargan en `02_seed.sql` con la contraseña hasheada con **bcrypt**. El backend debe verificarlos con `bcrypt.checkpw`.

| Correo | Contraseña | Rol |
|---|---|---|
| `admin@ucu.edu.uy` | `Admin2026!` | administrador |
| `planillero@ucu.edu.uy` | `Planillero2026!` | planillero |

### Usuarios de MySQL (permisos diferenciados)

Se crean en `01_schema.sql`. El backend elige la conexión según el rol del usuario logueado.

| Usuario | Contraseña | Permisos |
|---|---|---|
| `admin_app` | `Admin123!` | `SELECT, INSERT, UPDATE, DELETE` sobre toda la base |
| `planillero_app` | `Planilla123!` | `SELECT` en todo; `INSERT, UPDATE, DELETE` solo en `planilla_partido`, `gol` y `tarjeta`; `INSERT` en `sancion_jugador` |
| `login_app` | `Login123!` | `SELECT` solo sobre `login` (verifica correo y contraseña al iniciar sesión) |
| `root` | la de `.env` | Administración (no lo usa la app) |

## Datos de prueba

`02_seed.sql` carga una edición en curso (2026, semestre 2) pensada para ejecutar todos los reportes:

- 6 facultades, 5 turnos (18:00 a 23:00), 3 complejos y 5 canchas.
- 6 equipos con planteles de 7 a 9 jugadores (52 jugadores en total; 4 no integran ningún equipo).
- 16 partidos: fechas 1 a 4 jugadas (10 partidos), 1 cancelado, 1 postergado, fecha 5 programada y una reprogramación en la fecha 6.
- Planillas, 46 goles (incluye 2 autogoles) y 23 tarjetas.
- 5 sanciones: por roja, por acumulación de amarillas y disciplinaria. Ningún jugador suspendido figura en las planillas de las fechas que abarca su sanción.
- 7 jugadores de plantel que nunca figuraron en una planilla.

Cada partido del script lleva un comentario con su resultado, útil para comprobar la tabla de posiciones:

| Equipo | PJ | PG | PE | PP | GF | GC | DG | Pts |
|---|---|---|---|---|---|---|---|---|
| Psicología Sport Club | 4 | 3 | 1 | 0 | 13 | 6 | +7 | 10 |
| Salud Rovers | 4 | 3 | 0 | 1 | 13 | 5 | +8 | 9 |
| Derecho Atlético | 3 | 1 | 1 | 1 | 7 | 6 | +1 | 4 |
| Humanas Deportivo | 3 | 1 | 0 | 2 | 6 | 8 | -2 | 3 |
| Ingeniería FC | 4 | 1 | 0 | 3 | 5 | 13 | -8 | 3 |
| Empresariales United | 2 | 0 | 0 | 2 | 2 | 8 | -6 | 0 |

Humanas e Ingeniería empatan en puntos, así que el orden depende del desempate por diferencia de goles.

## Conexión a la base desde un cliente externo

Podés usar MySQL Workbench, DBeaver, DataGrip o la CLI de `mysql`:

| Parámetro | Valor |
|---|---|
| Host | `localhost` |
| Puerto | `3306` |
| Base de datos | `torneo_db` |
| Usuario | `root`, `admin_app`, `planillero_app` o `login_app` |

```bash
mysql -h 127.0.0.1 -P 3306 -u admin_app -p torneo_db
```

## Cómo funcionan los scripts de inicialización

Todo archivo `.sql` dentro de `./sql` se ejecuta **automáticamente y en orden alfabético**, pero **solo la primera vez**, cuando el volumen de datos está vacío. Por eso están numerados (`01_`, `02_`).

Si modificás un script y hacés `docker compose up` de nuevo, **los cambios no se aplican** sobre una base ya creada. Hay que reiniciarla desde cero (ver [Reiniciar la base desde cero](#reiniciar-la-base-desde-cero)).

`01_schema.sql` recrea la base (`DROP DATABASE IF EXISTS` + `CREATE DATABASE`) y `02_seed.sql` se ejecuta sobre ella, así que mantené el orden de los prefijos.

## Backend en modo desarrollo

El `docker-compose.yml` monta `./backend/app` dentro del contenedor y arranca uvicorn con `--reload`: al guardar un archivo del backend, el servidor se recarga solo, sin reconstruir la imagen.

Hay que reconstruir la imagen cuando cambia `requirements.txt` o el `Dockerfile`:

```bash
docker compose up -d --build backend
```

## Comandos útiles

| Acción | Comando |
|---|---|
| Levantar todo | `docker compose up -d --build` |
| Levantar solo la base | `docker compose up -d db` |
| Ver logs (todos) | `docker compose logs -f` |
| Ver logs del backend | `docker compose logs -f backend` |
| Reiniciar solo el backend | `docker compose restart backend` |
| Detener (conserva los datos) | `docker compose stop` |
| Volver a iniciar | `docker compose start` |
| Apagar y eliminar contenedores (conserva los datos) | `docker compose down` |
| Abrir consola MySQL | `docker compose exec db mysql -u root -p torneo_db` |
| Abrir shell en el backend | `docker compose exec backend sh` |

## Reiniciar la base desde cero

Para borrar todos los datos y volver a ejecutar los scripts de `./sql`:

```bash
docker compose down -v
docker compose up -d --build
```

> ⚠️ `-v` elimina el volumen `mysql_data`: se pierde **toda** la información de la base.

## Problemas frecuentes

**El puerto 3306 u 8000 ya está en uso**
Hay otro MySQL u otra aplicación corriendo en tu máquina. Detenela, o cambiá el mapeo en `docker-compose.yml` (el primer número es el de tu máquina):

```yaml
ports:
  - "3307:3306"   # db
  - "8001:8000"   # backend
```

El backend se conecta a la base por la red interna de Docker (`db:3306`), así que el cambio del puerto de la base no lo afecta.

**`/health/db` falla con `Access denied for user`**
Las contraseñas de `.env` no coinciden con las de `sql/01_schema.sql`, o los usuarios de MySQL no existen porque la base se creó antes de agregarlos. Corregí los valores y reiniciá desde cero con `docker compose down -v`.

**El backend arranca antes que la base y falla al conectar**
No debería pasar: el backend espera el healthcheck de `db`. Si ocurre, revisá `docker compose ps` (la base debe figurar como `healthy`) y `docker compose logs db`.

**`ValidationError` al arrancar el backend (field required)**
Falta alguna variable en `.env`. Compará con `.env.example`; el backend necesita las seis variables `DB_*`.

**Modifiqué un script SQL y no se aplicó**
Los scripts solo corren con el volumen vacío. Ver [Reiniciar la base desde cero](#reiniciar-la-base-desde-cero).

**Error de sintaxis en un script y la base no levanta**
Revisá `docker compose logs db`: MySQL indica el archivo y la línea del error. Corregilo y reiniciá desde cero.

**Caracteres raros (tildes, ñ)**
El contenedor arranca con `utf8mb4` y `utf8mb4_unicode_ci`. Verificá que tu cliente también use `utf8mb4`.

**`MYSQL_ROOT_PASSWORD` no definida**
Docker Compose muestra un warning y MySQL no arranca. Verificá que exista `.env` en la misma carpeta que `docker-compose.yml`.

**Windows: el hot reload no detecta cambios**
Si el repo está en una carpeta sincronizada o en una unidad de red, mové el proyecto al disco local (o dentro de WSL).