##Dia 1 - Listas y diccionarios
### Listas [] Mutable
# Indexación (indices | posicionamiento) >> str
# Positivos 0, ....
# Negativos -1, -2, ...
notas = [10, 9, 8, 7, 6] # 0 - 10 , 1 - 9, 2 - 8, 3 - 7, 4 - 6
                         # -5 -6, -4 -7, -3 -8, -2 -9, -1 -10
info = ["S2", "Python", 2024, True]
nombre = "Python"

print(f"Total de elementos: {len(notas)}") # 5
print(f"Primer elemento: {notas[0]}") # 10
print(f"Último elemento: {notas[-1]}") # 6

notas.append(5) # Agrega un elemento al final de la lista
print(f"Lista después de append: {notas}") # [10, 9, 8, 7, 6, 5]

print(nombre.lower()) # python
print(info[1].lower()) # python

nombre = "Python 3.11" + "Python 3.12"
print(nombre) # Python 3.11Python 3.12

notas_2 = [5, 4, 3, 2, 1]
notas_combinadas = notas + notas_2
print(f"Listas combinadas: {notas_combinadas}")
notas.extend(notas_2) # Agrega los elementos de notas_2 al final de notas
print(f"Notas después de extend: {notas}")

##TO-DO
# ¿Como agregar elementos a una lista en una posición especifica?
# Otras funciones  para usar en las listas
# ¿Como ordernar una lista?

### Diccionarios: {} - Par clave-valor Mutable
# Clave: Unica, Inmutable (str, int, float, bool, tupla)
estudiantes = {
    "100" : "Juan",
    "101" : "Maria",
    "102" : "Pedro",
    "103" : "Ana"
}

calificaciones = {
    "100": [10, 9, 8],
    "101": [9, 8, 7],
    "102": [8, 7, 6],
    "103": [7, 6, 5]
}

print(f"Total de estudiantes: {len(estudiantes)}") # 4
print(f"Nombre del estudiante con ID 101: {estudiantes['101']}") # Maria
estudiantes["104"] = "Luis" # Agrega un nuevo estudiante al diccionario
estudiantes.update({"105": "Sofia", "106": "Carlos"}) # Agrega múltiples estudiantes al diccionario
estudiantes.update({"100": "Sofia", "101": "Andres"}) # Actualiza los estudiantes existentes en el diccionario
print(f"Diccionario después de agregar estudiantes: {estudiantes}")

##Acceder a un Valor en un diccionario anidado
print(f"Estudiante {estudiantes['100']} - Calificaciones del estudiante con ID 100: {calificaciones['100']}") # [10, 9, 8]
print(f"Estudiante {estudiantes.get('101')} - Promedio de calificaciones del estudiante con ID 101: {sum(calificaciones['101']) / len(calificaciones['101']):.2f}") # 8.00

##TO-DO: .Keys(), .Values(), .Items()
#for para listas
for n in notas: # Itera sobre cada elemento de la lista notas y lo asigna a la variable n en cada iteración
    print(n)
for i in range(len(notas)): # Itera sobre un rango de números desde 0 hasta el número de elementos en la lista notas, y en cada iteración asigna el valor del índice a la variable i
    print(f"Índice: {i}, Nota: {notas[i]}")

## for para diccionarios
for clave, valor in estudiantes.items(): # Itera sobre cada par clave-valor en el diccionario estudiantes y asigna la clave a la variable clave y el valor a la variable valor en cada iteración, items comvierte el diccionario en una lista de tuplas (clave, valor)
    print(f"ID: {clave}, Nombre: {valor}")

for value in estudiantes.values(): # Itera sobre cada valor en el diccionario estudiantes y lo asigna a la variable value en cada iteración
    for i in range(len(value)): # Itera sobre un rango de números desde 0 hasta el número de caracteres en el valor actual del diccionario estudiantes, y en cada iteración asigna el valor del índice a la variable i
        print(f"Nombre: {value[i]}")    