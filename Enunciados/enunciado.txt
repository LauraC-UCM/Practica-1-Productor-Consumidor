Implementar un merge concurrente:
- Tenemos NPROD procesos que producen números no negativos de forma
creciente. Cuando un proceso acaba de producir, produce un -1. 
Cada proceso almacena el valor almacenado en una variable compartida con el consumidor,
un -2 indica que el almacén está vacío.

- Hay un proceso merge que debe tomar los números y almacenarlos de
forma creciente en una única lista (o array). El proceso debe esperar a que
los productores tengan listo un elemento e introducir el menor de
ellos.

- Se debe crear listas de semáforos. Cada productor solo maneja los
sus semáforos para sus datos. El proceso merge debe manejar todos los
semáforos.

- OPCIONAL: mente se puede hacer un búffer de tamaño fijo de forma que
los productores ponen valores en el búffer.
