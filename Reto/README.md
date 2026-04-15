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
cp config/.env
```

Edita `config/.env` con tus valores:
```
AGENCIA_API_KEY=tu_clave_secreta_aqui
EXTERNAL_API_URL=https://api.ejemplo.com
```

> ⚠️ El archivo `.env` **no se versiona**.

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
├── main.py                  # App FastAPI y endpoints
├── requirements.txt         # Dependencias del proyecto
├── Reto_Consolidacion.md    # Enunciado del reto
├── README.md                # Este archivo
│
├── models/                  # Clases de dominio (sin SQL ni FastAPI)
│   ├── __init__.py
│   └── agente.py            # PseudoAgente, AgenteAdmin
│
├── repository/              # Persistencia con SQLite
│   ├── __init__.py
│   └── db.py                # Funciones SQL (tablas, queries)
│
├── config/                  # Configuración
│   ├── __init__.py
│   └── .env                 # Variables de entorno (NO versionado)
│
└── service/                 # Lógica de negocio
    ├── __init__.py
    └── ...
```

---

## Cómo ejecutar

### Levantar el servidor (Terminal 1)

```bash
uvicorn main:app --reload
```

El flag `--reload` reinicia el servidor automáticamente cada vez que guardas cambios.
Deja esta terminal abierta.

### Abrir Swagger UI (Navegador)

Visita: [http://localhost:8000/docs](http://localhost:8000/docs)

Documentación interactiva generada por FastAPI. Desde aquí puedes probar cada endpoint.

### Ejecutar el cliente de demostración (Terminal 2)

Con el servidor corriendo en otra terminal:

```bash
python cliente.py
```

Este script ejecuta el flujo completo sin intervención manual:
1. Verifica que el servidor está vivo (`GET /`)
2. Crea un agente (`POST /agentes/`) con autenticación
3. Crea una misión asignada (`POST /misiones/`) con autenticación
4. Completa la misión (`POST /misiones/{id}/completar`) con autenticación
5. Consulta el briefing del agente (`GET /briefing/{nombre}`)
6. Envía un mensaje y lee la bandeja

---

## Tabla de endpoints

| Método | Ruta | Protegido | Descripción |
|--------|------|-----------|-------------|
| `GET` | `/` | No | Health check del servidor |
| `GET` | `/agentes/` | No | Lista todos los agentes |
| `GET` | `/agente/{nombre}` | No | Detalle de un agente |
| `POST` | `/agentes/` | Sí (API key) | Crea un agente nuevo |
| `POST` | `/mensajes/` | Sí (API key) | Envía un mensaje entre agentes |
| `GET` | `/mensajes/{nombre}` | No | Bandeja de mensajes de un agente |
| `POST` | `/misiones/` | Sí (API key) | Crea una misión asignada a un agente |
| `GET` | `/misiones/{id}` | No | Detalle de una misión |
| `GET` | `/agente/{nombre}/misiones` | No | Misiones asignadas a un agente |
| `POST` | `/misiones/{id}/completar` | Sí (API key) | Completa una misión (descuenta energía) |
| `GET` | `/briefing/{nombre}` | No | Briefing con datos locales + API externa |

Los endpoints protegidos requieren el header `X-API-KEY` con el valor configurado en `.env`.

---

## Decisiones de Ingeniería

### 1. Esquema de la tabla `misiones`
<!-- TODO: Justifica aquí qué columnas extra agregaste y por qué -->

### 2. API pública elegida
<!-- TODO: Justifica aquí cuál API elegiste, por qué encaja con la narrativa y qué añade al briefing -->

### 3. Estrategia de resiliencia
<!-- TODO: Justifica aquí qué pasa cuando la API externa falla o tarda -->

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
