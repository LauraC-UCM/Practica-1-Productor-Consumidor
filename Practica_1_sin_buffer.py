"""
PRACTICA 1 - PRODUCTOR/ CONSUMIDOR SIN BUFFER

(PRPA) Laura Cano Gómez

"""

from multiprocessing import Process
from multiprocessing import Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
import random


N = 3       # Veces que cada productor va a producir
NPROD = 3   # Número de productores


def delay(factor = 3):
    sleep(random.randint(1,4)/factor)

# Crea un producto y lo añade en su hueco de la lista de elementos producidos
def add_data(listaProducidos, pid, dataAnterior, mutex):

    mutex.acquire() # Esperamos a que la lista de productos se pueda editar
    try:
        dataNuevo= dataAnterior + random.randint(1, 10)
        listaProducidos[pid] = dataNuevo
        delay(6)

    finally:
        mutex.release() # Avisamos de que hemos acabado de editar la lista


# Elige qué producto se va a llevar el consumidor
def get_data(listaProducidos,mutex):
    mutex.acquire()
    try:
        indice:int
        primerMinimoElegido=False
        delay()
        for i in range(0,NPROD):
            if listaProducidos[i] > 0 and not primerMinimoElegido:
                minimoProducto= listaProducidos[i]
                indice=i
                primerMinimoElegido= True
            elif primerMinimoElegido:
                if listaProducidos[i] < minimoProducto  and listaProducidos[i] >0:
                    minimoProducto = listaProducidos[i]
                    indice=i

    finally:
        mutex.release()

    return minimoProducto, indice


# Comprueba si hay al menos un productor con productos disponibles
def siguenProduciendo(listaProducidos, mutex):
    mutex.acquire()
    siguen=False
    for i in range(NPROD):
        if(listaProducidos[i]>0):
            siguen=True
            break
    mutex.release()

    return siguen


def producer(listaProducidos, lSemPuedeProducir, lSemPuedeConsumir, mutex):
    pid=int(current_process().name.split('_')[1])   # Numero del productor actual
    dataAnterior= 0                                 # Variable para la primera vuelta, en la que la listaProducidos esta vacia (con -2)

    for i in range(N):
        delay(6)

        # Esperamos hasta que el consumidor haga un signal informando de que se ha llevado su producto
        lSemPuedeProducir[pid].acquire() 
        print (f"{current_process().name} produciendo...")

        add_data(listaProducidos, pid, dataAnterior, mutex) # Crea un producto y lo añade en su hueco de la lista
        dataAnterior= listaProducidos[pid]
        
        lSemPuedeConsumir[pid].release()

        print (f"El {current_process().name} ha fabricado {dataAnterior}.")

    # Al  salir del for, ya habra producido N veces asi que la siguiente producirá -1 y acabará el proceso
    lSemPuedeProducir[pid].acquire()
    mutex.acquire()
    listaProducidos[pid]=-1
    print (f"El {current_process().name} ha terminado de producir. (-1)")
    mutex.release()
    lSemPuedeConsumir[pid].release()


def consumer(listaProducidos, lSemPuedeProducir, lSemPuedeConsumir, mutex, listaConsumidos, contadorConsumidos): 
    # Espera a que los NPROD hayan producido algo
    for i in range(NPROD):
        lSemPuedeConsumir[i].acquire()
    
    # Mientras haya productos disponibles, consumimos
    while siguenProduciendo(listaProducidos, mutex):
        print ("Comprador llegando...")
        minimoProducto, indiceProductor= get_data(listaProducidos,mutex) # Elige a quién va a comprarle su producto 
        
        listaConsumidos[contadorConsumidos.value]= minimoProducto
        contadorConsumidos.value += 1

        print (f"El consumidor compra el producto {minimoProducto} del productor {indiceProductor}.")      

        # El productor al que se lo acabamos de comprar puede volver a producir, y el consumidor espera a que acabe de hacerlo
        lSemPuedeProducir[indiceProductor].release()
        lSemPuedeConsumir[indiceProductor].acquire()

        delay()


def main():
    listaProducidos= Array('i', NPROD)    # Lista con los productos producidos. La posicion i corresponde al productor i.
    listaConsumidos= Array('i', NPROD*N)  # Lista con los productos consumidos.
    contadorConsumidos = Value('i', 0)    # Contador para saber el numero de veces que el consumidor ha comprado
    
    # Inicializo la produccion a -2 (vacio)
    for i in range(NPROD):
        listaProducidos[i] = -2
    print ("Almacen inicial:", listaProducidos[:])

    
    # Semáforos requeridos:
    lSemPuedeConsumir = [Semaphore(0) for i in range(NPROD)]    # Regula que todos los procesos tienen almacenado un producto, para que el consumidor pueda acceder (el non_empty) (el 0 es para que se inicialice en rojo)
    lSemPuedeProducir = [Lock() for j in range(NPROD)]          # Regula que el productor tenga hueco para producir (el empty)
    mutex = Lock()                                              # Regula el acceso a la lista de productos producidos (solo puede haber una persona editandola al mismo tiempo)


    # Creo un proceso por cada productor
    procesosProductores = [ Process(target=producer,
                                    name=f'Productor_{i}',
                                    args=(listaProducidos, lSemPuedeProducir, lSemPuedeConsumir, mutex))
                            for i in range(NPROD) ]


    # Creo el proceso pedido "merge", siendo este la accion del consumidor
    merge = Process(target=consumer,
                    args=(listaProducidos, lSemPuedeProducir, lSemPuedeConsumir, mutex, listaConsumidos, contadorConsumidos))


    # Puesta en marcha de los procesos creados
    for p in procesosProductores:
        p.start()
    
    merge.start()

    for p in procesosProductores:
        p.join()

    merge.join()

    # Resultados obtenidos:
    print ("\nUltima produccioón: ", listaProducidos[:])
    print ("\nProductos vendidos: ", listaConsumidos[:])

if __name__ == '__main__':
    main()
