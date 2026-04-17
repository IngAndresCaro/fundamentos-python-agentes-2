# 🏛️ La Agencia de Agentes — Reto de Consolidación

## Preparación del entorno

> **Tip:** Para ver este archivo renderizado en VS Code: `Ctrl + Shift + V`
  **Tip:** Recuerda que las credenciales básicas son las ya manejadas con anterioridad y están en base de datos user por si las requieres

### 1. Crea el entorno virtual

**Windows:**
```bash
python -m venv .venv
```

**macOS / Linux:**
```bash
python3 -m venv .venv
```

### 2. Activa el entorno virtual

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

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 4. Configura las variables de entorno

Copia el archivo de ejemplo y completa los valores:

```bash
cp config/.env.example config/.env
```

Edita `config/.env` con tus valores:
```
AGENCIA_API_KEY=tu_clave_secreta_aqui
API_ADVICE_URL=https://api.adviceslip.com/advice
API_JOKE_URL=https://v2.jokeapi.dev/joke/Programming?type=single&lang=es
API_WIKIPEDIA_URL=https://en.wikipedia.org/api/rest_v1/page/random/summary
```

> ⚠️ El archivo `config/.env` **no se versiona**. Solo se versiona `.env.example`.

### 5. Verifica la instalación

```bash
python -c "import fastapi; print('FastAPI', fastapi.__version__, '- OK')"
python -c "import requests; print('Requests - OK')"
python -c "from dotenv import load_dotenv; print('python-dotenv - OK')"
```

---

## Estructura del proyecto

```
├── main.py                        # App FastAPI, middleware de sesión, dashboard
├── requirements.txt               # Dependencias: fastapi, uvicorn, requests, python-dotenv, python-multipart
├── .env.example                   # Plantilla de variables de entorno (se versiona)
├── README.md                      # Este archivo
│
├── domain/                        # 🧠 Comportamiento — clases de dominio puras
│   ├── __init__.py
│   └── agentes.py                 # PseudoAgente, AgenteAdmin, AgenteOrquestador, AgenteSpec,
│                                  # AgenteBackend, AgenteFrontend, AgenteQA (herencia, polimorfismo)
│
├── schemas/                       # 📐 Tipado — esquemas Pydantic para request/response
│   ├── __init__.py
│   └── agente.py                  # CrearAgenteBody, ActualizarAgenteBody, EnviarMensajeBody, CrearMisionBody
│
├── repository/                    # 💾 Persistencia — solo SQL, sin FastAPI
│   ├── __init__.py
│   ├── db.py                      # Funciones CRUD para agentes, mensajes, misiones + auth
│   ├── sbom.py                    # SBOM con 7 componentes + CPE 2.3 (para escaneo NVD)
│   ├── agentes.db                 # Base de datos principal (agentes, mensajes, misiones, cache_cves)
│   └── user.db                    # Base de datos de usuarios del sistema (login)
│
├── config/                        # ⚙️ Configuración centralizada
│   ├── __init__.py
│   ├── settings.py                # Carga .env, exporta AGENCIA_API_KEY y URLs de APIs externas
│   └── .env                       # Variables de entorno reales (NO versionado)
│
├── api/                           # 🔌 Endpoints — routers FastAPI por dominio
│   ├── __init__.py
│   ├── agentes.py                 # CRUD de agentes + mensajes (/api/agentes, /api/mensajes)
│   ├── misiones.py                # CRUD de misiones + completar con R2 (/api/misiones)
│   ├── briefing.py                # Briefing con API externa (§5.2) (/api/briefing)
│   ├── seguridad.py               # Agente Smit: escaneo SBOM, NVD/GitHub Advisory, cache CVEs
│   └── auth_routes.py             # Login/logout con formulario HTML (/login, /logout)
│
├── core/                          # 🔐 Seguridad y sesiones
│   ├── __init__.py
│   ├── security.py                # Dependencia verificar_api_key (§5.1)
│   └── session.py                 # Gestión de sesiones en memoria (token → rol)
│
├── templates/                     # 🎨 Presentación — HTML
│   ├── __init__.py
│   ├── dashboard.py               # Template HTML: oficina animada con zonas y agentes
│   └── login.py                   # Template HTML: formulario de login
│
├── tests/                         # 🧪 Tests de integración (pytest + httpx)
│   └── test_integracion.py        # 9 tests: API key, briefing, flujo completo R5
│
├── .github/                       # 🤖 Framework ASD — Agentes IA especializados
│   ├── agents/                    # 9 agentes (.agent.md): orchestrator, spec, backend, frontend, qa, GAIDD
│   ├── prompts/                   # 9 prompts (.prompt.md): puntos de entrada para cada agente
│   ├── skills/                    # 14 skills (.md): QA (8), Backend (3), Frontend (3)
│   ├── docs/                      # Contexto: config, arquitectura, lineamientos, output
│   ├── copilot-instructions.md    # Instrucciones globales para Copilot
│   └── INDEX.md                   # Inventario completo de componentes y relaciones
│
├── img/                           # 📸 Capturas de pantalla para evidencia visual
│
└── tests/                         # 🧪 Tests de integración (pytest + httpx)
    └── test_integracion.py        # 9 tests: API key, briefing, flujo completo R5
```

### Separación `domain/` vs `schemas/`

| Carpeta | Propósito | Contiene |
|---------|-----------|----------|
| `domain/` | **Comportamiento** (dominio puro) | `PseudoAgente`, `AgenteAdmin`, `AgenteOrquestador`, `AgenteSpec`, `AgenteBackend`, `AgenteFrontend`, `AgenteQA` — energía, historial, polimorfismo de `consumir_energia()` |
| `schemas/` | **Tipado** (validación de datos) | Esquemas Pydantic (`BaseModel`) — validan la forma de los JSON que recibe la API |

Esta separación permite que `domain/agentes.py` no dependa de FastAPI/Pydantic, y que `schemas/agente.py` no tenga lógica de negocio.

---

## Cómo ejecutar

### Levantar el servidor

```bash
python -m uvicorn main:app --reload
```

> En Windows con Git Bash, si Python no está en PATH:
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
| `GET` | `/api/agentes/{nombre}` | Sí (sesión / API key) | Detalle de un agente (incluye `tipo_agente`, `es_admin`, `experiencia`) |
| `POST` | `/api/agentes` | Sí (API key) | Crea un agente nuevo |
| `PUT` | `/api/agentes/{nombre}` | Sí (API key) | Actualiza rol y/o energía de un agente |
| `DELETE` | `/api/agentes/{nombre}` | Sí (API key) | Elimina un agente (solo si no tiene misiones activas) |
| `GET` | `/api/agentes/{nombre}/estado-eliminacion` | Sí (sesión / API key) | Verifica si el agente puede eliminarse |

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
| `POST` | `/api/misiones/{mision_id}/completar` | Sí (API key) | Completa una misión (R2: polimorfismo + suma XP de recompensa) |

### Briefing (`/api/briefing`)

| Método | Ruta | Protegido | Descripción |
|--------|------|-----------|-------------|
| `GET` | `/api/briefing/{nombre}` | No | Briefing: datos del agente + resumen misiones + inteligencia externa según rol |

---

## R2 — Clases de dominio y jerarquía de agentes

Los agentes del sistema están basados en el framework ASD (`.github/agents/`). Al "despertar" un agente desde la base de datos, se reconstruye como instancia de la clase correcta usando `reconstruir_desde_datos()`:

```python
# domain/agentes.py — reconstruir_desde_datos()
MAPA_ROLES_CLASE = {
    "admin": AgenteAdmin,
    "orquestador": AgenteOrquestador,
    "spec": AgenteSpec,
    "backend": AgenteBackend,
    "frontend": AgenteFrontend,
    "qa": AgenteQA,
}

def reconstruir_desde_datos(datos: dict) -> PseudoAgente:
    clase = MAPA_ROLES_CLASE.get(datos["rol"], PseudoAgente)
    return clase(nombre=datos["nombre"], energia=datos["energia"])
```

### Jerarquía de agentes y consumo energético

| Clase | Rol | Energía | Basado en |
|-------|-----|---------|-----------|
| `PseudoAgente` | (base) | 100% | — |
| `AgenteAdmin` | `admin` | 50% | `agent_orchestrator` (coordinador) |
| `AgenteOrquestador` | `orquestador` | 30% | `agent_orchestrator` (pipeline GAIDD) |
| `AgenteSpec` | `spec` | 70% | `agent_spec` (análisis de requerimientos) |
| `AgenteBackend` | `backend` | 100% | `agent_backend` (implementación) |
| `AgenteFrontend` | `frontend` | 100% | `agent_frontend` (implementación) |
| `AgenteQA` | `qa` | 80% | `agent_qa` (testing) |

El polimorfismo de `consumir_energia()` decide el costo real sin lógica en el endpoint.

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

Los agentes se representan con iconos según su rol (🎯 orquestador, 📋 spec, ⚙️ backend, 🎨 frontend, 🧪 qa, 👔 admin) y tienen una barra de energía visual con indicador de experiencia (`⭐ N XP`). Al hacer clic en un agente se despliega su detalle con misiones asignadas y recompensas.

Los botones de la barra lateral dependen del rol:
- **Admin**: crear agente, nueva misión, enviar mensaje, completar misión, recargar agente, eliminar agente + consultas.
- **Invitado**: solo consultas (misiones, mensajes y briefing de un agente).

---

## Decisiones de Ingeniería

### 1. Esquema de la tabla `misiones`

Se agregaron dos columnas extra al esquema mínimo:

- **`prioridad TEXT DEFAULT 'media'`** — Permite clasificar misiones por urgencia (`baja`, `media`, `alta`, `critica`). En una agencia real, no todas las misiones tienen la misma importancia; la prioridad permite ordenar y filtrar. Se muestra en el dashboard para dar contexto visual al operador.
- **`updated_at TEXT`** — Registra cuándo cambió el estado por última vez (ISO 8601). Complementa a `created_at` para saber no solo cuándo se creó la misión sino cuándo se completó o modificó. Útil para auditoría y para mostrar timestamps en el dashboard.

### 2. APIs públicas elegidas (inteligencia por rol)

En lugar de una sola API externa, se implementaron **3 APIs diferenciadas según el rol** del agente, simulando fuentes de inteligencia especializadas:

| Rol | API | Tono |
|-----|-----|------|
| qa, spec | [Advice Slip](https://api.adviceslip.com/) | Empático (consejo motivacional) |
| backend, admin | [Wikipedia Featured](https://en.wikipedia.org/api/rest_v1/) | Profesional (artículo destacado del día) |
| orquestador, frontend, otros | [JokeAPI Programming](https://v2.jokeapi.dev/) | Divertido (chiste de programación en español) |

Si el agente tiene misiones de seguridad, se activa además el **Agente Smit** que consulta NVD NIST y GitHub Advisory (ver sección Agente Smit).

### 3. Estrategia de resiliencia

Se implementó un timeout de **3 segundos** en la llamada a la API externa con `requests.get(..., timeout=3)`. Si la API falla (timeout, error de red, SSL, status != 200), se captura la excepción con `try/except` y se devuelve un mensaje de fallback: `"[Fallback] La fuente de inteligencia no está disponible."`, junto con la fuente marcada como `(error)`. Se registra un `logger.warning(...)` para auditar el fallo. De esta forma, el endpoint `/api/briefing/{nombre}` **siempre responde** con los datos locales del agente, sin dejar que un tercero cuelgue el servidor.

### 4. Columnas `recompensa` y `experiencia`

- **`misiones.recompensa INTEGER DEFAULT 10`** — Cada misión tiene una recompensa en XP configurable al crearla. Al completar la misión, los puntos se suman a la experiencia del agente.
- **`agentes.experiencia INTEGER DEFAULT 0`** — Acumula los XP ganados al completar misiones. Se muestra en el dashboard como `⭐ N XP` junto a la barra de energía.

Esto añade progresión a los agentes: no solo pierden energía al trabajar, también ganan experiencia.

### 5. Validadores Pydantic v2 (`@field_validator`)

Se añadieron validadores con `@field_validator` (Pydantic v2) en los modelos de entrada:

- **`CrearAgenteBody.rol`** — Normaliza a minúsculas y valida contra roles permitidos (`orquestador`, `spec`, `backend`, `frontend`, `qa`, `admin`).
- **`CrearMisionBody.energia_positiva`** — Rechaza energía ≤ 0.
- **`CrearMisionBody.prioridad_valida`** — Valida contra prioridades permitidas (`baja`, `media`, `alta`, `critica`).
- **`ActualizarAgenteBody.rol`** — Mismo validador de rol (solo si se proporciona).

---

## Limpieza

```bash
# Borrar la base de datos (se regenera al ejecutar de nuevo)
rm repository/agentes.db

# Desactivar el entorno virtual
deactivate
```

---

## Ejecutar tests (Reto Eutagógico — pytest)

No necesita servidor corriendo. Los tests usan `TestClient` de FastAPI (in-process):

```bash
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

## Agente Smit — Escaneo de Seguridad

Cuando un agente tiene misiones con palabras clave de seguridad (`seguridad`, `vulnerabilidad`, `exploit`, `pentesting`, `amenaza`, etc.), el briefing activa al **Agente Smit**, que realiza un escaneo automático:

1. **SBOM** — 7 componentes del proyecto (Python, FastAPI, Uvicorn, Starlette, Pydantic, Requests, SQLite) con identificadores CPE 2.3.
2. **NVD NIST API v2.0** — Consulta vulnerabilidades conocidas por CPE.
3. **GitHub Advisory Database** — Consulta complementaria por ecosistema (`pip`).
4. **Filtrado CVSS ≥ 7.0** — Solo muestra alertas de severidad HIGH o CRITICAL.
5. **Caché SQLite** — Tabla `cache_cves` con TTL de 1 hora para no repetir consultas.
6. **Retry con backoff exponencial** — Ante 503/403/429, reintenta con espera progresiva.
7. **Recomendaciones dinámicas** — Genera sugerencias según los CVEs encontrados.

Al finalizar el escaneo, las misiones de seguridad se auto-completan y el agente gana XP.

---

## Reto Eutagógico — Los 3 caminos completados

### Opción A: CRUD completo

Se implementaron los endpoints `PUT` y `DELETE` que complementan el CRUD básico:

- **`PUT /api/agentes/{nombre}`** — Actualiza rol y/o energía con `ActualizarAgenteBody` (campos opcionales).
- **`DELETE /api/agentes/{nombre}`** — Elimina un agente solo si no tiene misiones activas (pendientes o en curso).
- **`GET /api/agentes/{nombre}/estado-eliminacion`** — Verifica previamente si el agente puede eliminarse.

### Opción B: Validadores Pydantic v2

Se añadieron `@field_validator` en los modelos de entrada para validar roles, prioridades y energía antes de llegar a la base de datos (ver Decisión de Ingeniería #5).

### Opción C: Tests con pytest

9 tests de integración organizados en 3 clases (ver sección "Ejecutar tests").

---

## Pistas de investigación — Qué es cada una y dónde se usó

| Pista de investigación | Qué es | ¿Se usó? | Dónde |
|------------------------|--------|----------|-------|
| `"FastAPI api key header dependency"` | Cómo crear una dependencia (`Depends`) en FastAPI que lee un header personalizado (`X-API-KEY`) para proteger endpoints. | ✅ Sí | `core/security.py` → función `verificar_api_key` inyectada con `Depends` en todos los endpoints `/api/`. |
| `"fastapi Depends header authentication"` | Mecanismo de inyección de dependencias de FastAPI (`Depends`) combinado con `Header()` para extraer y validar headers HTTP. | ✅ Sí | `core/security.py` → `x_api_key: str = Header(default="")` como parámetro de la dependencia. |
| `"python-dotenv load_dotenv"` | Librería que carga variables desde un archivo `.env` al entorno del proceso (`os.environ`), evitando hardcodear secretos en el código. | ✅ Sí | `config/settings.py` → `from dotenv import load_dotenv` + `load_dotenv(dotenv_path=...)`. |
| `"os.environ getenv default value"` | Función `os.getenv("CLAVE", "valor_por_defecto")` del módulo estándar para leer variables de entorno con fallback seguro. | ✅ Sí | `config/settings.py` → `os.getenv("AGENCIA_API_KEY", "...")` para todas las variables. |
| `"python logging basicConfig levels formatter"` | Módulo estándar `logging` con `basicConfig()` para configurar niveles (INFO/WARNING/ERROR), formato de fecha y mensaje estructurado. | ✅ Sí | `main.py` → `logging.basicConfig(level=INFO, format="%(asctime)s [%(levelname)s] %(message)s")`. |
| `"requests timeout exception handling"` | Parámetro `timeout` en `requests.get(url, timeout=N)` y manejo de excepciones (`Timeout`, `ConnectionError`, `RequestException`) para no bloquear el servidor. | ✅ Sí | `api/briefing.py` → `requests.get(url, timeout=3)` con `try/except` y fallback. |
| `"public APIs list no auth github"` | Repositorios en GitHub que listan APIs públicas gratuitas sin autenticación (JSON). Se usó para elegir las fuentes de inteligencia externa. | ✅ Sí | 3 APIs: [Advice Slip](https://api.adviceslip.com/), [JokeAPI](https://v2.jokeapi.dev/), [Wikipedia REST](https://en.wikipedia.org/api/rest_v1/). |
| `"pydantic v2 field_validator"` | Decorador `@field_validator` de Pydantic v2 para validar campos individuales de un `BaseModel` antes de que lleguen a la lógica de negocio. | ✅ Sí | `schemas/agente.py` → validadores de `rol`, `energia_requerida > 0` y `prioridad`. |
| `"fastapi TestClient pytest"` | Clase `TestClient` de FastAPI que permite testear endpoints sin levantar servidor real, combinada con `pytest` para tests automatizados. | ✅ Sí | `tests/test_integracion.py` → 9 tests con `TestClient(app)` + `unittest.mock.patch`. |

## Referencias consultadas

- [FastAPI — Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI — Header Parameters](https://fastapi.tiangolo.com/tutorial/header-params/)
- [Pydantic v2 — Validators](https://docs.pydantic.dev/latest/concepts/validators/)
- [python-dotenv — Documentation](https://saurabh-kumar.com/python-dotenv/)
- [Python logging — Basic Tutorial](https://docs.python.org/3/howto/logging.html)
- [Requests — Timeouts](https://requests.readthedocs.io/en/latest/user/advanced/#timeouts)
- [Advice Slip API](https://api.adviceslip.com/)
- [JokeAPI](https://v2.jokeapi.dev/)
- [Wikipedia REST API](https://en.wikipedia.org/api/rest_v1/)
- [NVD NIST API v2.0](https://nvd.nist.gov/developers/vulnerabilities)
- [GitHub Advisory Database](https://github.com/advisories)

---

## Evidencia visual

![Swagger UI — Endpoints](img/image.png)

![Swagger UI — Detalle](img/image-1.png)

![Dashboard — Oficina animada](img/image-2.png)