# Practica-1-Productor-Consumidor

Implementación de un merge concurrente:

Parte 1: 
  - Tenemos NPROD procesos que producen números no negativos de forma creciente. Cuando un proceso acaba de producir, produce un -1. Cada proceso almacena el valor almacenado en una variable compartida con el consumidor, un 2 indica que el almacén está vacío.

  - Hay un proceso merge que debe tomar los números y almacenarlos de forma creciente en una única lista (o array). El proceso debe esperar a que los productores tengan listo un elemento e introducir el menor de ellos.

  - Se debe crear listas de semáforos. Cada productor solo maneja sus semáforos para sus datos. El proceso merge debe manejar todos los semáforos.

Parte2: 
  - Hacer un búffer de tamaño fijo de forma que los productores ponen valores en el búffer.


## Archivos
 
 - **Practica_1_sin_buffer.py** solución a la Parte 1
 - **Practica_1_con_buffer.py** solución a la Parte 2

## Ejecución
Parte 1: python3 Practica_1_sin_buffer

Parte 2: python3 Practica_1_con_buffer


## CORRECCIONES HECHAS
- Readme completado
- Archivos .py sin espacios
- Incluidas líneas 95, 99 y 106 en el archivo _Practica_1_con_buffer.py_
    - Línea 95: mutex.acquire () # Controla que el acceso a listaProducidos sea seguro
    - Línea 99: comentario
    - Línea 106: mutex.release()
