# 🛠️ Taller Semana 3: Forjando las Herramientas (Refactorización y Blindaje)

**Fecha límite de entrega:** Lunes 30 marzo, 2026, 23h59.

**Forma de entrega:** Pull-Request a la rama `semana_3` desde sus repositorios forkeados.

## 🎯 Contexto
Nuestro PseudoAgente es funcional, pero su cerebro (el bucle `while` principal) se ha convertido en un bloque de código gigante y difícil de mantener. En la industria de la IA, a los modelos (LLMs) no se les pasa un bucle `while`; se les pasa una lista de **Herramientas (Tools)** bien definidas.

Tu misión en este sprint es refactorizar el código de la Semana 2, extrayendo la lógica pesada hacia funciones independientes, tipadas y blindadas contra errores.

## 📋 Requerimientos Funcionales

Tu archivo principal debe ser reestructurado siguiendo estos pasos:

### 1. Definición del Contrato de Memoria (Type Aliasing)
Antes de crear tus funciones, debes definir la "forma" que tiene la memoria de tu Agente. En clase vimos el use de la palaba `type`.
* Crea un **Alias de Tipo** para un recuerdo individual. Como sabemos que las llaves (ej. "rol", "mensaje") son texto y los valores también, defínelo así: `Recuerdo = Dict[str, str]`.
* Crea un alias para tu historial completo: `MemoriaAgente = List[Recuerdo]`.
* *Nota:* A partir de ahora, cuando una función necesite el historial, no le pedirás un simple `list`, le pedirás una `MemoriaAgente`.

### 2. Refactorización (Creación de Tools)
Extrae la lógica de tus comandos hacia al menos **dos funciones puras**. El bloque `if/elif` del menú `while` ahora solo debe encargarse de capturar el input del usuario e invocar a estas funciones.

* **Tool A: `gestionar_historial(...)`**
  * Esta función debe recibir la acción del usuario (`"all"`, `"clear"`, o la palabra a buscar) y la memoria actual (usando tu Type Hint `memoria: MemoriaAgente`).
  * Debe **retornar** un `str` (texto) con el resultado formateado (ya sea la confirmación de borrado, todo el historial, o los resultados de búsqueda). 
  * *Importante:* No usar `print()` dentro de esta función. La herramienta procesa datos y los devuelve; el bucle principal es quien se encarga de imprimirlos.

* **Tool B: Comandos complejos (`contar_letras(...)`, `calculadora(...)`, `validar_password(...)` , etc.)**
  * Extrae los comandos de contar, validar_pass y calculadora en funciones. Debe estar perfectamente tipada (parámetros y valor de retorno) y tener su respectivo *Docstring* `""" """` explicando qué hace cada una.

### 3. Blindaje contra el Caos (Manejo de Errores)
Debes implementar al menos un bloque `try/except` robusto en tu código. 
* Investiga cómo usar la palabra reservada `raise` para disparar una excepción nativa de Python (como `PermissionError` o `ValueError`).
  * **El Reto:** Modifica el comando `fecha_hoy`. Si un usuario con rol `"invitado"` intenta usarlo, tu código debe ejecutar `raise PermissionError("Privilegios insuficientes")`. 
* Atrapa esta excepción usando un `try/except` en tu bucle principal para mostrar la alerta bonita en la consola sin que el programa crashee.
* Identifica **otro punto crítico** donde el programa podría fallar por un mal input del usuario y reescríbelo para utilizar un `try/except`.
* **Prohibido usar `except:` desnudo.** Debes atrapar el error específico (ej. `ValueError`) y devolver un mensaje elegante para que el PseudoAgente no se apague.

## 🤖 Política de Vibecoding y Evaluación
Puedes usar la IA para que te sugiera cómo extraer el código o cómo aplicar los Type Hints. Sin embargo, el evaluador serás tú.

**Regla de Auditoría:** Debes dejar un comentario (`#`) con tus propias palabras exactamente encima de:
1. **Tus Alias de Tipos:** Explica por qué darle un "Alias" a la estructura de datos (`MemoriaAgente`) ayuda cuando trabajamos con modelos de IA.
2. **Tu bloque `raise`:** Explica cómo viaja el error desde que lo "lanzas" (raise) dentro de tu lógica hasta que lo "atrapas" (except) en tu menú.

*Nota: Un código con funciones que carecen de Type Hints en su firma (ej. `def mi_func(a) -> None:`), o que no usan `return`, sufrirá penalizaciones en la revisión.*