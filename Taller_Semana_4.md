# 🛠️ Taller Semana 4: Nace la Entidad (POO y Modularización)

**Fecha límite de entrega:** Lunes 6 abril, 2026, 23h59.

**Forma de entrega:** Pull-Request a la rama `semana_4` desde sus repositorios forkeados.

## 🎯 Contexto
¡Felicidades! En la Semana 3 lograste crear herramientas sólidas y blindadas. Sin embargo, tu código sigue siendo un script procedimental donde el "estado" (el historial y el usuario) flota globalmente. 

En la industria del software, un Agente de IA no es un conjunto de funciones sueltas, es una **Entidad** con memoria propia y recursos limitados. En este sprint, vamos a transformar tu código usando Programación Orientada a Objetos (POO) y organizaremos el proyecto en múltiples archivos (Módulos).

## 📋 Requerimientos Funcionales

Tu proyecto ahora dejará de ser un solo archivo kilométrico. Debes estructurarlo cumpliendo los siguientes pasos:

### 1. Modularización (Separación de Archivos)
Crea una arquitectura de dos archivos en tu proyecto:
* `agente.py`: Aquí vivirá exclusivamente tu nueva Clase `PseudoAgente` y tus Alias de Tipos.
* `main.py`: Aquí vivirá tu sistema de Login y tu menú `while`. 
* En tu `main.py`, debes importar la clase usando: `from agente import PseudoAgente`.

### 2. El Molde: La Clase `PseudoAgente`
Dentro de `agente.py`, debes encapsular tus funciones de la Semana 3 convirtiéndolas en **Métodos de Instancia**.
* **El Constructor (`__init__`):** Tu clase debe inicializarse recibiendo el `nombre` del agente. Además, debe inicializar su propio estado interno: `self.tokens = 100` y `self.historial_chat: MemoriaAgente = []`.
* **Adaptación de Herramientas:** Convierte tus funciones anteriores (`gestionar_historial`, `contar_letras`, `fecha_hoy`, etc.) en métodos agregando el parámetro `self`.
* *¡Atención!* Ya no necesitas pasarle la memoria como parámetro a `gestionar_historial`. El método ahora debe usar directamente `self.historial_chat`.

### 3. El Desgaste (Modificación de Estado)
Un objeto vivo consume recursos. 
* Cada vez que se ejecute un comando (ping, contar, calculadora, etc.), el método respectivo debe gestionar el **consumo de tokens** a `self.tokens` (ej. -5 por historial, -2 por ping, etc). Todos los comandos deben hacer un consumo razonable, queda de forma libre la definición de estos.
* Si `self.tokens` llega a `0` o menos, el Agente debe negarse a trabajar lanzando un error o devolviendo un mensaje de agotamiento. En tu `main.py`, el `while` debe monitorear esto y apagarse si el agente "muere" de cansancio. IMPORTANTE: No utilizar `break` para gestionar la salida del bucle.

### 4. Uso de Librerías Estándar
Tu agente necesita interactuar con herramientas externas del sistema.
* Utiliza el módulo `datetime` para el comando `fecha_hoy` y para estampar la hora en los registros de tu historial.
* **Nueva Herramienta:** Importa el módulo estándar `random`. Crea un nuevo método llamado `lanzar_dado(self) -> str` que consuma poca batería y devuelva un número aleatorio entre 1 y 6.

## 🧠 Reto Eutagógico (Autodidacta): Especialización por Herencia
Los Agentes reales suelen tener versiones "Pro" o especializadas. 
* Investiga cómo funciona la **Herencia** en Python y qué es el método `super().__init__()`.
* Crea una segunda clase en `agente.py` llamada `AgenteAdmin` que herede de `PseudoAgente`.
* **El Reto:** Sobreescribe el método `gestionar_historial` en esta nueva clase hija. Para el `AgenteAdmin`, revisar el historial **no debe consumir batería**.
* En tu `main.py`, al hacer el login: Si el usuario es "admin", instancia un `AgenteAdmin`. Si es "invitado", instancia un `PseudoAgente` normal. 

## 🤖 Política de Vibecoding y Evaluación
La POO puede ser confusa al principio. Usa IA para entender los errores de "missing 1 required positional argument: 'self'".

**Regla de Auditoría:** Debes dejar un comentario (`#`) con tus propias palabras exactamente encima de:
1. **Tu bloque de Herencia:** Explica en 2 líneas por qué crear un `AgenteAdmin` que hereda de `PseudoAgente` es mejor que copiar y pegar todo el código en una clase nueva.
2. **Tu método `__init__`:** Explica la diferencia entre una variable temporal dentro de una función y una variable que empieza con `self.`.

*Nota: Entregas que sigan teniendo la variable `historial_chat` flotando en el `while` de `main.py` en lugar de estar encapsulada en la clase, no serán aprobadas.*