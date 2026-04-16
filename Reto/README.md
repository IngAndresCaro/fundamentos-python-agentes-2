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
│   ├── briefing_service.py        # Briefing con API externa (§5.2) (/api/briefing)
│   └── cliente_service.py         # Login/logout con formulario HTML (/login, /logout)
│
├── src/                           # 🎨 Presentación — HTML, sesiones
│   ├── __init__.py
│   ├── auth.py                    # Dependencia verificar_api_key (§5.1)
│   ├── dashboard.py               # Template HTML: oficina animada con zonas y agentes
│   ├── cliente.py                  # Template HTML: formulario de login
│   └── session.py                 # Gestión de sesiones en memoria (token → rol)
│
└── cliente.py                     # R5: Script HTTP de demostración end-to-end
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
| `GET` | `/api/agentes` | Sí (sesión / API key) | Lista todos los agentes |
| `GET` | `/api/agentes/{nombre}` | Sí (sesión / API key) | Detalle de un agente (incluye `tipo_agente` y `es_admin`) |
| `POST` | `/api/agentes` | Sí (API key) | Crea un agente nuevo |

### Mensajes (`/api/mensajes`)

| Método | Ruta | Protegido | Descripción |
|--------|------|-----------|-------------|
| `POST` | `/api/mensajes` | Sí (API key) | Envía un mensaje entre agentes |
| `GET` | `/api/mensajes/{nombre_agente}` | Sí (sesión / API key) | Bandeja de mensajes de un agente |

### Misiones (`/api/misiones`)

| Método | Ruta | Protegido | Descripción |
|--------|------|-----------|-------------|
| `POST` | `/api/misiones` | Sí (API key) | Crea una misión asignada a un agente |
| `GET` | `/api/misiones/{nombre_agente}` | Sí (sesión / API key) | Misiones asignadas a un agente |
| `GET` | `/api/misiones/detalle/{mision_id}` | Sí (sesión / API key) | Detalle de una misión por ID |
| `POST` | `/api/misiones/{mision_id}/completar` | Sí (API key) | Completa una misión (R2: descuenta energía con polimorfismo) |

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

Al completar una misión (`POST /api/misiones/{id}/completar`):
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

Se eligió la API de **Useless Facts** (`https://uselessfacts.jsph.pl/api/v2/facts/random`). Encaja con la narrativa de la agencia porque simula un canal de "inteligencia externa": cada briefing incluye un dato curioso del mundo real, como si el agente recibiera información de una fuente externa de inteligencia. Es una API pública sin autenticación, gratuita, con respuestas rápidas en JSON, lo que la hace ideal para un entorno de desarrollo y demostración.

### 3. Estrategia de resiliencia

Se implementó un timeout de **3 segundos** en la llamada a la API externa con `requests.get(..., timeout=3)`. Si la API falla (timeout, error de red, SSL, status != 200), se captura la excepción con `try/except` y se devuelve un mensaje de fallback: `"[Fallback] La fuente de inteligencia no está disponible."`, junto con la fuente marcada como `(error)`. Se registra un `logger.warning(...)` para auditar el fallo. De esta forma, el endpoint `/api/briefing/{nombre}` **siempre responde** con los datos locales del agente, sin dejar que un tercero cuelgue el servidor.

Qué pasa cuando la API externa falla o tarda? esta responde que no pudo ejecutar la respuesta, sacando un error soportado, puede pasar que el tiempo es muy corto en el equipo que estamos por seguridad no podemos ingresar o este mismo este caido
¿Tu agente responde con un mensaje de fallback, omite el campo, o devuelve un error?  devuelve un fallback
¿Por qué? esto para que el usuario no se quede sin información ya que el no reconoce codigo y aun no hemos conectado a chatsInteligentes para que nos den una respuesta mas amena a lo que buscamos

---

## Limpieza

```bash
# Borrar la base de datos (se regenera al ejecutar de nuevo)
rm repository/agentes.db

# Desactivar el entorno virtual
deactivate
```

---

### Briefing (`/api/briefing`)

| Método | Ruta | Protegido | Descripción |
|--------|------|-----------|-------------|
| `GET` | `/api/briefing/{nombre}` | No | Briefing: datos del agente + resumen misiones + inteligencia externa |

---

## Ejecutar cliente de demostración (R5)

Con el servidor corriendo en otra terminal:

```bash
# Terminal 1 — servidor
uvicorn main:app --reload --port 8000

# Terminal 2 — cliente
python cliente.py
# o especificando puerto:
python cliente.py --port 8001
```

El script ejecuta automáticamente los 6 pasos del guion R5:

1. Verifica que el servidor está vivo (`GET /api/agentes`).
2. Crea dos agentes con `X-API-KEY` (`POST /api/agentes`).
3. Crea una misión asignada (`POST /api/misiones`).
4. Completa la misión (`POST /api/misiones/{id}/completar`).
5. Consulta el briefing (`GET /api/briefing/{nombre}`).
6. Envía un mensaje y lee la bandeja (`POST /api/mensajes` + `GET /api/mensajes/{nombre}`).

---

## Ejecutar tests (Reto Eutagógico — pytest)

No necesita servidor corriendo. Los tests usan `TestClient` de FastAPI (in-process):

```bash
# Desde la carpeta Reto/
python -m pytest tests/ -v
```

**9 tests** organizados en 3 clases:

| Clase | Tests | Qué valida |
|-------|-------|------------|
| `TestProteccionApiKey` | 4 | Endpoints POST sin `X-API-KEY` → rechazados (agentes, misiones, completar, mensajes) |
| `TestBriefing` | 3 | Estructura con mock de API externa, fallback cuando falla, 404 si agente no existe |
| `TestFlujoCompletoR5` | 2 | Circuito completo R5 end-to-end + R2 polimorfismo (admin paga mitad energía) |

La API externa se mockea con `unittest.mock.patch` para que los tests no dependan de red.

---

## Referencias consultadas

- [FastAPI — Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI — Header Parameters](https://fastapi.tiangolo.com/tutorial/header-params/)
- [python-dotenv — Documentation](https://saurabh-kumar.com/python-dotenv/)
- [Python logging — Basic Tutorial](https://docs.python.org/3/howto/logging.html)
- [Requests — Timeouts](https://requests.readthedocs.io/en/latest/user/advanced/#timeouts)
- [Useless Facts API](https://uselessfacts.jsph.pl/)

