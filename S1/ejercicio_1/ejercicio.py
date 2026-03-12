"""Mini-taller I: Ejercicio para práctica autónoma"""
### La IA generó un sistema de cálculo de bonos, pero está crasheando
# tomando decisiones ilógicas. ¿Puedes encontrar los 3 errores
# arreglarlos y mejorar los prints usando f-strings?
sueldo = float(input("Ingresa tu sueldo base: "))
anios_empresa = int(input("¿Cuántos años llevas en la empresa?: "))

bono = sueldo * 0.10

if anios_empresa > 5:
    print("¡Felicidades! Tienes un bono extra por antigüedad.")
    total = sueldo + bono + 500
else:
    print("No hay bono de antigüedad.")
    total = sueldo + bono

print(f"Tu total a recibir es: {total}")
