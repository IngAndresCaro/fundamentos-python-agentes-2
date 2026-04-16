# 🏛️ La Agencia de Agentes — Reto de Consolidación

## Preparación del entorno

### 1. Navega a la carpeta del reto

```bash
cd Reto
```

### 2. Crea el entorno virtual

**Windows:**
```bash
python -m venv .venv
```

**macOS / Linux:**
```bash
python3 -m venv .venv
```

### 3. Activa el entorno virtual

**Windows (Git Bash):**
```bash
source .venv/Scripts/activate
```

**Windows (cmd):**
```cmd
.venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

Sabrás que está activo porque verás `(.venv)` al inicio de tu línea de terminal.

### 4. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 5. Configura las variables de entorno

Copia el archivo de ejemplo y completa los valores:

```bash
cp .env.example config/.env
```

Edita `config/.env` con tus valores:
```
AGENCIA_API_KEY=tu_clave_secreta_aqui
EXTERNAL_API_URL=https://uselessfacts.jsph.pl/api/v2/facts/random
```

> ⚠️ El archivo `config/.env` **no se versiona**. Solo se versiona `.env.example`.

### 6. Verifica la instalación

```bash
python -c "import fastapi; print('FastAPI', fastapi.__version__, '- OK')"
python -c "import requests; print('Requests - OK')"
python -c "from dotenv import load_dotenv; print('python-dotenv - OK')"
```

---

## Estructura del proyecto

```
Reto/
├── main.py                        # App FastAPI, middleware de sesión, dashboard
├── requirements.txt               # Dependencias: fastapi, uvicorn, requests, python-dotenv, python-multipart
├── .env.example                   # Plantilla de variables de entorno (se versiona)
├── Reto_Consolidacion.md          # Enunciado del reto
├── README.md                      # Este archivo
│
├── agentes/                       # 🧠 Comportamiento — clases de dominio puras
│   ├── __init__.py
│   └── agente.py                  # PseudoAgente, AgenteAdmin (herencia, polimorfismo)
│
├── models/                        # 📐 Tipado — esquemas Pydantic para request/response
│   ├── __init__.py
│   └── agente.py                  # CrearAgenteBody, EnviarMensajeBody, CrearMisionBody
│
├── repository/                    # 💾 Persistencia — solo SQL, sin FastAPI
│   ├── __init__.py
│   ├── db.py                      # Funciones CRUD para agentes, mensajes, misiones + auth
│   ├── agentes.db                 # Base de datos principal (agentes, mensajes, misiones)
│   └── user.db                    # Base de datos de usuarios del sistema (login)
│
├── config/                        # ⚙️ Configuración centralizada
│   ├── __init__.py
│   ├── config.py                  # Carga .env, exporta AGENCIA_API_KEY y EXTERNAL_API_URL
│   └── .env                       # Variables de entorno reales (NO versionado)
│
├── service/                       # 🔌 Endpoints — routers FastAPI por dominio
│   ├── __init__.py
│   ├── agente_service.py          # CRUD de agentes + mensajes (/api/agentes, /api/mensajes)
│   ├── mision_service.py          # CRUD de misiones + completar con R2 (/api/misiones)
│   └── cliente_service.py         # Login/logout con formulario HTML (/login, /logout)
│
└── src/                           # 🎨 Presentación — HTML, sesiones
    ├── __init__.py
    ├── dashboard.py               # Template HTML: oficina animada con zonas y agentes
    ├── cliente.py                  # Template HTML: formulario de login
    └── session.py                 # Gestión de sesiones en memoria (token → rol)
```

### Separación `agentes/` vs `models/`

| Carpeta | Propósito | Contiene |
|---------|-----------|----------|
| `agentes/` | **Comportamiento** (dominio puro) | `PseudoAgente`, `AgenteAdmin` — energía, historial, polimorfismo de `consumir_energia()` |
| `models/` | **Tipado** (validación de datos) | Esquemas Pydantic (`BaseModel`) — validan la forma de los JSON que recibe la API |

Esta separación permite que `agentes/agente.py` no dependa de FastAPI/Pydantic, y que `models/agente.py` no tenga lógica de negocio.

---

## Cómo ejecutar

### Levantar el servidor

```bash
# Desde la carpeta Reto/
uvicorn main:app --reload --port 8000
```

> En Windows con Git Bash, si `uvicorn` no está en PATH:
> ```bash
> ".venv/Scripts/python.exe" -m uvicorn main:app --reload --port 8000
> ```

El flag `--reload` reinicia el servidor automáticamente al guardar cambios. Deja esta terminal abierta.

### Acceder a la aplicación

| URL | Descripción |
|-----|-------------|
| [http://localhost:8000/login](http://localhost:8000/login) | Formulario de login (punto de entrada) |
| [http://localhost:8000/](http://localhost:8000/) | Dashboard con oficina animada (requiere sesión) |
| [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger UI — solo accesible con rol **admin** |
| [http://localhost:8000/redoc](http://localhost:8000/redoc) | ReDoc — solo accesible con rol **admin** |

### Credenciales de prueba

| Usuario | Contraseña | Rol | Permisos |
|---------|------------|-----|----------|
| `admin` | `admin123` | admin | Dashboard completo, Swagger, crear/completar misiones |
| `invitado` | `1234` | invitado | Dashboard solo lectura, consultar agentes y misiones |

---

## Tabla de endpoints

### Autenticación (sesión con cookies)

| Método | Ruta | Protegido | Descripción |
|--------|------|-----------|-------------|
| `GET` | `/login` | No | Formulario HTML de login |
| `POST` | `/login` | No | Valida credenciales, crea sesión, redirige a `/` |
| `GET` | `/logout` | No | Cierra sesión y redirige a `/login` |

### Dashboard

| Método | Ruta | Protegido | Descripción |
|--------|------|-----------|-------------|
| `GET` | `/` | Sí (sesión) | Dashboard con oficina animada según rol |

### Agentes (`/api/agentes`)

| Método | Ruta | Protegido | Descripción |
|--------|------|-----------|-------------|
| `GET` | `/api/agentes` | Sí (sesión) | Lista todos los agentes |
| `GET` | `/api/agentes/{nombre}` | Sí (sesión) | Detalle de un agente (incluye `tipo_agente` y `es_admin`) |
| `POST` | `/api/agentes` | Sí (sesión) | Crea un agente nuevo |

### Mensajes (`/api/mensajes`)

| Método | Ruta | Protegido | Descripción |
|--------|------|-----------|-------------|
| `POST` | `/api/mensajes` | Sí (sesión) | Envía un mensaje entre agentes |
| `GET` | `/api/mensajes/{nombre_agente}` | Sí (sesión) | Bandeja de mensajes de un agente |

### Misiones (`/api/misiones`)

| Método | Ruta | Protegido | Descripción |
|--------|------|-----------|-------------|
| `POST` | `/api/misiones` | Sí (sesión) | Crea una misión asignada a un agente |
| `GET` | `/api/misiones/{nombre_agente}` | Sí (sesión) | Misiones asignadas a un agente |
| `GET` | `/api/misiones/detalle/{mision_id}` | Sí (sesión) | Detalle de una misión por ID |
| `PUT` | `/api/misiones/{mision_id}/completar` | Sí (sesión) | Completa una misión (R2: descuenta energía con polimorfismo) |

---

## R2 — Clases de dominio reutilizadas

Al "despertar" un agente desde la base de datos, se reconstruye como instancia de la clase correcta:

```python
# service/mision_service.py — reconstruir_agente()
datos = despertar_agente(nombre)          # dict desde SQLite
if datos["rol"] == "admin":
    agente = AgenteAdmin(nombre=..., energia=...)
else:
    agente = PseudoAgente(nombre=..., energia=...)
```

Esto garantiza que `isinstance(agente, AgenteAdmin)` sea `True` cuando corresponde, y que el polimorfismo de `consumir_energia()` funcione:

- **PseudoAgente**: descuenta el 100% de la energía requerida.
- **AgenteAdmin**: descuenta solo el 50% (override en la subclase).

Al completar una misión (`PUT /api/misiones/{id}/completar`):
1. Se lee la misión de la DB.
2. Se reconstruye la instancia de dominio del agente asignado.
3. Se llama a `agente.consumir_energia(energia_requerida)` — **la clase decide el costo**.
4. Se persiste la nueva energía y se marca la misión como completada.

---

## Dashboard — La Oficina

Al iniciar sesión, el usuario ve una oficina animada con tres zonas donde los agentes se mueven:

| Zona | Color | Criterio |
|------|-------|----------|
| 💼 **Trabajando** | Verde | Agentes con misiones pendientes |
| 😴 **Holgazaneando** | Rojo | Agentes sin misiones y energía > 50 |
| 🎮 **Recreándose** | Azul | Agentes sin misiones y energía ≤ 50 |

Los agentes se representan con iconos según su rol (🕵️ espía, 📊 analista, 🛡️ guardián, 👔 admin) y tienen una barra de energía visual. Al hacer clic en un agente se despliega su detalle con misiones asignadas.

Los botones de la barra lateral dependen del rol:
- **Admin**: crear agente, nueva misión, enviar mensaje, completar misión + consultas.
- **Invitado**: solo consultas (misiones y mensajes de un agente).

---

## Decisiones de Ingeniería

### 1. Esquema de la tabla `misiones`

Se agregaron dos columnas extra al esquema mínimo:

- **`prioridad TEXT DEFAULT 'media'`** — Permite clasificar misiones por urgencia (`baja`, `media`, `alta`, `critica`). En una agencia real, no todas las misiones tienen la misma importancia; la prioridad permite ordenar y filtrar. Se muestra en el dashboard para dar contexto visual al operador.
- **`updated_at TEXT`** — Registra cuándo cambió el estado por última vez (ISO 8601). Complementa a `created_at` para saber no solo cuándo se creó la misión sino cuándo se completó o modificó. Útil para auditoría y para mostrar timestamps en el dashboard.

### 2. API pública elegida
<!-- TODO: Justifica aquí cuál API elegiste, por qué encaja con la narrativa y qué añade al briefing -->

### 3. Estrategia de resiliencia
<!-- TODO: Justifica aquí qué pasa cuando la API externa falla o tarda -->

---

## Requerimientos pendientes

- [ ] **5.1** Autenticación con API key (`X-API-KEY` header) para endpoints de escritura
- [ ] **5.2** Endpoint `GET /briefing/{nombre}` con integración de API pública externa
- [ ] **R5** `cliente.py` — script de demostración end-to-end con `requests`
- [ ] Datos semilla: 3 agentes, 5 mensajes, 3 misiones en estados distintos
- [ ] Evidencias visuales (capturas Swagger: 401 sin key, 201 con key, briefing)

---

## Limpieza

```bash
# Borrar la base de datos (se regenera al ejecutar de nuevo)
rm repository/agentes.db

# Desactivar el entorno virtual
deactivate
```

---

## Referencias consultadas
<!-- TODO: Agrega enlaces a la documentación y artículos que consultaste -->
