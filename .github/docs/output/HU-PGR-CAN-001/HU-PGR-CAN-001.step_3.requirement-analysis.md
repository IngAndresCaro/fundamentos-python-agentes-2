# Especificación Técnica — PGR: Cancelación Masiva de Tareas en Proceso
**Versión:** 1.3.0
**Fecha:** 2026-03-16
**Estado:** Aprobada
**Generado por:** Spec Agent · Revisado por: PO / Scrum Master
**Fuente de contexto:** [PGR - Documentación General](https://segurosti.atlassian.net/wiki/spaces/EDO/pages/3215065132/PGR+-+Documentaci%C3%B3n+General)

> **Decisión PO (2026-03-16):** Alcance reducido a un único mecanismo — cancelación **masiva** mediante carga de archivo desde `/cargas/cancelacion-masiva`. La cancelación individual queda fuera de este entregable.

---

## Resumen Ejecutivo

El sistema **PGR** (Plan de Trabajo Para la Gestión de Riesgos) permite gestionar planes de trabajo, asignación de tareas a asesores y el seguimiento de servicios orientados a ambientes de trabajo seguros para la ARL - CGR.

**Problema identificado:** No existe una interfaz que permita al Administrador GesPrevencion ejecutar cancelaciones masivas de tareas en estado `PROCESANDO` mediante la carga de un archivo, utilizando el endpoint existente `CANCELACION_TAREAS`.

**Alcance de este entregable (limitado por PO):**
- ✅ Subir archivo de cancelación masiva desde `/cargas/cancelacion-masiva`
- ✅ Ejecutar la cancelación masiva consumiendo el endpoint existente `CANCELACION_TAREAS`
- ❌ Fuera de alcance: cancelación individual por tarea, estado intermedio, aprobación multinivel, notificaciones, re-apertura

---

## Análisis de Requerimientos

```
📋 SPEC AGENT — ANÁLISIS DE REQUERIMIENTOS
════════════════════════════════════════════════
Proyecto detectado:   PGR — Plan de Trabajo Gestión de Riesgos
Stack tecnológico:    Spring WebFlux · Java 8 · MongoDB (Backend)
                      Angular 9 · NgRx · Nx (Frontend)
Estado actual:        Endpoint de carga masiva CANCELACION_TAREAS ya existente.
                      No existe página Frontend para consumirlo.

Requerimientos identificados:
  Funcionales:
    1. Admin GesPrevencion accede a /cargas/cancelacion-masiva
    2. Sube archivo con las tareas a cancelar
    3. Ejecuta la cancelación invocando el endpoint existente
    4. Visualiza el resultado (tareas canceladas / errores)
  No funcionales:
    - Seguridad: solo ADMINISTRADOR_GESPREVENCION accede a la ruta y endpoint
    - Trazabilidad: la carga registra quién y cuándo subió el archivo (backend existente)
  Restricciones:
    - Endpoint backend ya existe — NO crear endpoint nuevo
    - Solo aplica a tareas en estado PROCESANDO
    - Actor único: ADMINISTRADOR_GESPREVENCION

Ambigüedades resueltas por PO:
  ✅ Solo cancelación masiva — la cancelación individual queda fuera de este entregable
  ✅ El trabajo es Frontend únicamente (backend ya implementado)
════════════════════════════════════════════════
```

---

## Historia de Usuario

```
─────────────────────────────────────────────────
HU-PGR-CAN-001: Cancelación masiva de tareas en proceso
─────────────────────────────────────────────────
Como:        Administrador GesPrevencion
Quiero:      Subir un archivo de cancelación masiva desde
             /cargas/cancelacion-masiva y ejecutarlo para cancelar
             múltiples tareas en estado PROCESANDO en un solo paso
Para:        Resolver bloqueos operativos a escala sin tener que
             gestionar tarea por tarea, reduciendo el tiempo
             operativo del equipo

Prioridad:   Alta
Estimación:  M
Dependencias: Ninguna
Capa:        Solo Frontend (endpoint backend ya existe)

URL Frontend: /cargas/cancelacion-masiva
Endpoint:     POST /api/v1/gestion-plan-trabajo/carga/CANCELACION_TAREAS/tipoUsuario/ADMINISTRADOR_GESPREVENCION
─────────────────────────────────────────────────
```

---

## Criterios de Aceptación

```
═══════════════════════════════════════════════
HU-PGR-CAN-001: Cancelación masiva de tareas en proceso
CRITERIOS DE ACEPTACIÓN
═══════════════════════════════════════════════

# Happy Path
CRITERIO-1.1: Carga y ejecución exitosa de cancelación masiva
  Dado que:  El Administrador GesPrevencion está autenticado y navega
             a /cargas/cancelacion-masiva
  Cuando:    Selecciona el archivo con las tareas a cancelar
             y hace clic en "Subir y ejecutar cancelación"
  Entonces:  El sistema envía el archivo al endpoint existente
             CANCELACION_TAREAS/tipoUsuario/ADMINISTRADOR_GESPREVENCION,
             muestra el resultado con el número de tareas canceladas
             y mensaje "Cancelación masiva ejecutada exitosamente"

# Error Path
CRITERIO-1.2: Archivo con formato inválido
  Dado que:  El Administrador sube un archivo con formato incorrecto
             o campos faltantes
  Cuando:    El endpoint responde con error de validación
  Entonces:  El sistema muestra el detalle de errores retornado por
             el backend (filas/tareas con problema)
             y no cancela las tareas con error

CRITERIO-1.3: Intento de carga sin archivo seleccionado
  Dado que:  El Administrador hace clic en "Subir y ejecutar"
             sin haber seleccionado un archivo
  Cuando:    Intenta confirmar la acción
  Entonces:  El sistema muestra validación client-side
             "Debe seleccionar un archivo para continuar"
             y no realiza ninguna llamada al backend

CRITERIO-1.4: Acceso por usuario sin rol ADMINISTRADOR_GESPREVENCION
  Dado que:  Un usuario con rol diferente intenta acceder
             a /cargas/cancelacion-masiva
  Cuando:    Navega a la URL
  Entonces:  El sistema redirige al usuario a la pantalla de
             acceso denegado (HTTP 403)

# Edge Case
CRITERIO-1.5: Error de comunicación durante la carga masiva
  Dado que:  El Administrador sube el archivo y el backend no responde
             (timeout o error 500)
  Cuando:    El endpoint retorna error
  Entonces:  El sistema muestra "Error al procesar la cancelación masiva.
             Intente nuevamente." conservando el archivo para reintento
═══════════════════════════════════════════════
```

---

## Contratos de API

```
─────────────────────────────────────────────────
CONTRATO-1: Cancelación masiva de tareas (EXISTENTE — solo consume Frontend)
HU relacionada: HU-PGR-CAN-001
─────────────────────────────────────────────────
Endpoint:       POST /api/v1/gestion-plan-trabajo/carga/CANCELACION_TAREAS/tipoUsuario/ADMINISTRADOR_GESPREVENCION
Base URL:       https://apigestionprevencionlab.labsura.com
Autenticación:  Bearer JWT
Roles:          ADMINISTRADOR_GESPREVENCION
Descripción:    Endpoint EXISTENTE. Recibe archivo de cancelación masiva
                tipo CANCELACION_TAREAS. El Frontend CONSUME — no implementa.

REQUEST:
  Headers:
    Content-Type: multipart/form-data
    Authorization: Bearer {token}
  Path Params:
    tipoCarga   → "CANCELACION_TAREAS"             (fijo en la URL)
    tipoUsuario → "ADMINISTRADOR_GESPREVENCION"    (fijo en la URL)
  Body (multipart):
    archivo → File  // Formato definido por backend existente

RESPONSE EXITOSO (200 OK):
  (Verificar estructura real con equipo backend en staging)
  {
    "success": true,
    "data": {
      "totalProcesadas": 0,
      "canceladasExitosamente": 0,
      "conErrores": 0,
      "errores": []
    },
    "message": "Cancelación masiva ejecutada exitosamente",
    "timestamp": "ISO8601"
  }

RESPONSES DE ERROR:
  400 | INVALID_FILE_FORMAT | Formato incorrecto  | "El archivo no tiene el formato esperado"
  403 | FORBIDDEN           | Rol sin permiso     | "No tiene permisos para ejecutar cancelaciones masivas"
  500 | INTERNAL_ERROR      | Error no controlado | "Error interno del servidor. Intente nuevamente."

⚠️  Validar respuesta exacta del endpoint con backend antes de implementar Frontend.
─────────────────────────────────────────────────
```

---

## Arquitectura Propuesta

```
🏗️ ARQUITECTURA PROPUESTA
════════════════════════════════════════════════

PATRÓN ARQUITECTURAL: Microservicios (existente)
JUSTIFICACIÓN: El endpoint de carga CANCELACION_TAREAS ya existe en
               ms-gestion-plan-trabajo. Solo se implementa el módulo
               Frontend de la página /cargas/cancelacion-masiva.

COMPONENTES INVOLUCRADOS:
─────────────────────────────────────────────────
ms-gestion-plan-trabajo (Backend — SIN CAMBIOS)
  Endpoint activo:
    POST /api/v1/gestion-plan-trabajo/carga/CANCELACION_TAREAS/
         tipoUsuario/ADMINISTRADOR_GESPREVENCION
  ⚠️  NO requiere cambios de backend en este entregable.

pgr-frontend (Frontend — Angular 9 / NgRx / Nx)
  URL: /cargas/cancelacion-masiva
  Cambios requeridos:
    - Ruta /cargas/cancelacion-masiva registrada en el router Angular
      (verificar si el módulo /cargas ya existe como lazy module)
    - Route Guard: solo ADMINISTRADOR_GESPREVENCION accede a la ruta
    - Componente CancelacionMasivaComponent:
        · Input file para selección de archivo
        · Botón "Subir y ejecutar cancelación" (deshabilitado sin archivo)
        · Panel de resultados: total procesadas / exitosas / con error
        · Tabla de detalle de errores por fila (si el backend los retorna)
    - Actions/Reducers/Effects/Selectors NgRx para el flujo de carga masiva
    - Manejo de estados: cargando / éxito / error

SEGURIDAD:
  Autenticación: JWT Bearer (existente)
  Autorización:  ADMINISTRADOR_GESPREVENCION (Route Guard Angular +
                 validación server-side en el endpoint existente)
  Validación client-side: archivo seleccionado antes de enviar

RIESGOS TÉCNICOS:
  - Respuesta del endpoint puede diferir del contrato asumido:
    Mitigación → validar estructura real en staging antes de implementar Frontend
  - Tiempos de respuesta largos para cargas grandes:
    Mitigación → spinner + deshabilitar botón durante procesamiento
                 para evitar doble envío
════════════════════════════════════════════════
```

---

## Diseño de Flujo Frontend (NgRx)

```
FLUJO — CANCELACIÓN MASIVA:
  1. Admin GesPrevencion navega a /cargas/cancelacion-masiva
     → Route Guard valida rol ADMINISTRADOR_GESPREVENCION
  2. Componente renderiza: input file + botón "Subir y ejecutar" (deshabilitado)
  3. Admin selecciona archivo → botón se habilita
     → dispatch SeleccionarArchivoAction({ archivo })
  4. Clic "Subir y ejecutar cancelación"
     → dispatch EjecutarCancelacionMasivaAction({ archivo })
  5. Effect → POST /api/v1/gestion-plan-trabajo/carga/CANCELACION_TAREAS/
                         tipoUsuario/ADMINISTRADOR_GESPREVENCION
     → estado "cargando": spinner visible, botón deshabilitado
  6. Success → dispatch EjecutarCancelacionMasivaSuccessAction({ resultado })
              → panel de resultados: total procesadas / exitosas / con error
              → tabla de errores si los hay
  7. Error → dispatch EjecutarCancelacionMasivaFailureAction
            → toast "Error al procesar la cancelación masiva. Intente nuevamente."
            → archivo conservado para reintento
```

---

## Definition of Ready — Checklist

Antes de que el equipo comience el desarrollo, verificar:

- [ ] Rol ADMINISTRADOR_GESPREVENCION disponible y verificable en el JWT
- [ ] **Formato del archivo de carga `CANCELACION_TAREAS` documentado por backend**
- [ ] **Estructura de respuesta del endpoint validada en staging**
- [ ] Ruta `/cargas` confirmada como módulo existente en el router Angular
- [ ] Diseño UI/UX de la página `/cargas/cancelacion-masiva` aprobado por PO
- [ ] Acceso a `https://apigestionprevencionlab.labsura.com` disponible desde Frontend en staging

---

## Definition of Done — Checklist

Para la HU, la historia está DONE cuando:

- [ ] Criterios 1.1 al 1.5 superados (automatizados o manuales)
- [ ] Ruta `/cargas/cancelacion-masiva` registrada y protegida con Route Guard
- [ ] Componente `CancelacionMasivaComponent` implementado con NgRx
- [ ] Validación client-side: archivo requerido antes de enviar
- [ ] Panel de resultados con detalle de errores visible
- [ ] Manejo de estados loading / success / error en Frontend
- [ ] Accesibilidad WCAG 2.1 AA en formulario de carga (aria-labels, foco)
- [ ] PR con checklist completo aprobado por 1 revisor
- [ ] Sin deuda técnica nueva introducida

---

## Contexto de Referencia del Proyecto

| Elemento | Valor |
|---|---|
| Sistema | PGR — Plan de Trabajo Para la Gestión de Riesgos |
| Organización | ARL - CGR (Segurosti) |
| Backend stack | Spring WebFlux 2.2.7 · Java 8 · MongoDB |
| Frontend stack | Angular CLI 9.1 · NgRx · Nx Devtools · Karma/Jasmine |
| URL Frontend cancelación masiva | https://gestionprevencionlab.labsura.com/cargas/cancelacion-masiva |
| Endpoint cancelación masiva | https://apigestionprevencionlab.labsura.com/api/v1/gestion-plan-trabajo/carga/CANCELACION_TAREAS/tipoUsuario/ADMINISTRADOR_GESPREVENCION |
| Confluence | PGR - Documentación General (espacio EDO) |
| PO / Scrum Master | Andres Felipe Caro Gonzalez |
