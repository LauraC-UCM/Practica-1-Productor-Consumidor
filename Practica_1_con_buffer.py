"""
PRACTICA 1 - PRODUCTOR/ CONSUMIDOR CON BUFFER

(PRPA) Laura Cano Gómez

"""


from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
import random


NPROD = 3   # Número de productores
N = 5       # Veces que cada productor va a producir
K= 4        # Tamaño del buffer de cada productor


# Retraso para la ejecucion de los procesos
def delay(factor = 3):
    sleep(random.randint(1,4)/factor)


# Crea un producto y lo añade en el buffer del productor correspondiente, en la lista de elementos producidos
def add_data(listaProducidos, pid, dataAnterior, mutex, indicesProducir):

    mutex.acquire() # Esperamos a que la lista de productos se pueda editar
    try:
        dataNuevo= dataAnterior + random.randint(1, 10)
        listaProducidos[pid][indicesProducir[pid]] = dataNuevo
        indicesProducir[pid]= (indicesProducir[pid] + 1) % K    # Mueve el indice al siguiente para que este bien colocado en la proxima vuelta
        delay(6)

    finally:
        mutex.release() # Avisamos de que hemos acabado de editar la lista de productos


# Devuelve qué producto se va a llevar el consumidor y a qué productor corresponde
def get_data(listaProducidos,mutex, indicesConsumir):
    mutex.acquire()
    try:
        pid:int #pid= indiceDelPorductor actual
        primerMinimoElegido=False
        delay()
        for i in range(0,NPROD):
            producto=listaProducidos[i][indicesConsumir[i]]
            if producto > 0 and not primerMinimoElegido:
                minimoProducto= producto
                pid=i
                primerMinimoElegido= True
            elif primerMinimoElegido:
                if producto < minimoProducto  and producto >0:
                    minimoProducto = producto
                    pid=i

        listaProducidos[pid][indicesConsumir[pid]]=-2
        indicesConsumir[pid]= (indicesConsumir[pid]+1) % K  # Mueve el indice al siguiente para que este bien colocado en la proxima vuelta

    finally:
        mutex.release()

    return minimoProducto, pid


# Comprueba si hay al menos un productor con productos disponibles
def siguenProduciendo(listaProducidos, mutex, indicesConsumir):
    mutex.acquire()
    siguen=False
    for i in range(NPROD):
        if(listaProducidos[i][indicesConsumir[i]]>0):
            siguen=True
            break
    mutex.release()

    return siguen


def producer(listaProducidos, lSemPuedeProducir, lSemPuedeConsumir, mutex, indicesProducir):
    pid=int(current_process().name.split('_')[1])   # Numero del productor actual
    dataAnterior= 0                                 # Variable para la primera vuelta, en la que la listaProducidos esta vacia (con -2)

    for i in range(N):
        delay(6)

        # Esperamos hasta que el consumidor haga un signal informando de que se ha llevado su producto
        lSemPuedeProducir[pid].acquire() 

        print (f"{current_process().name} produciendo...")

        add_data(listaProducidos, pid, dataAnterior, mutex, indicesProducir) # Crea un producto y lo añade en su hueco de la lista

        mutex.acquire() # Controla que el acceso a listaProducidos sea seguro    

        '''
        Comentario del profesor, esto es también una regíón crítica.
        Comentario alumna: se añaden las líneas 95 y 106 para solventar el problema de ser region críica
        '''
        dataAnterior= listaProducidos[pid][(indicesProducir[pid]-1) % K]
        
        print (f"El {current_process().name} ha fabricado {dataAnterior}.")
        print (f"El buffer del {current_process().name} es {listaProducidos[pid][:]}.")
       
        mutex.release()

        lSemPuedeConsumir[pid].release()

    # Al  salir del for, ya habra producido N veces asi que la siguiente producirá -1 y acabará el proceso
    lSemPuedeProducir[pid].acquire()
    mutex.acquire()
    listaProducidos[pid][indicesProducir[pid]]=-1
    print (f"El {current_process().name} ha terminado de producir. (-1)")
    mutex.release()
    lSemPuedeConsumir[pid].release()


def consumer(listaProducidos, lSemPuedeProducir, lSemPuedeConsumir, mutex, listaConsumidos, contadorConsumidos, indicesConsumir): 
    # Esperamos a que los NPROD hayan producido algo
    for i in range(NPROD):
        lSemPuedeConsumir[i].acquire()
    
    # Mientras haya productos disponibles, consumimos
    while siguenProduciendo(listaProducidos, mutex, indicesConsumir):
        print ("Comprador llegando...")
        minimoProducto, pid= get_data(listaProducidos,mutex, indicesConsumir) # Elige a quién va a comprarle su producto 

        listaConsumidos[contadorConsumidos.value]= minimoProducto
        contadorConsumidos.value += 1

        print (f"El consumidor compra el producto {minimoProducto} del productor {pid}.")      

        # El productor al que se lo acabamos de comprar puede volver a producir, y el consumidor espera a que acabe de hacerlo
        lSemPuedeProducir[pid].release()
        lSemPuedeConsumir[pid].acquire()

        delay()


def main():
    listaConsumidos= Array('i', NPROD*N)    # Lista con los productos consumidos.
    contadorConsumidos = Value('i', 0)      # Contador para saber el numero de veces que el consumidor ha comprado
    
    # Lista con los productos producidos (se inicializa con -2). La posicion i corresponde al buffer del productor i.
    listaProducidos=[]
    for i in range(NPROD):
        buffer=Array('i', K) 
        listaProducidos.append(buffer)
        for j in range(K):      # Inicializo las componentes de los buffer a -2 para que quede más claro visualmente en la ejecucion
            listaProducidos[i][j]=-2
        

    # Indices para la listaProducidos, la posicion i corresponde al productor i
    indicesConsumir = Array('i', N)  # Lugar con el primer producto (para que el consumidor se lo lleve)
    indicesProducir = Array('i', N)  # Lugar con el primer hueco libre (para que el productor lo ponga ahi)


    # Semáforos requeridos:
    lSemPuedeConsumir = [Semaphore(0) for i in range(NPROD)]            # Regula que todos los procesos tienen almacenado un producto, para que el consumidor pueda acceder (el non_empty) (el 0 es para que se inicialice en rojo)
    lSemPuedeProducir = [BoundedSemaphore(K) for j in range(NPROD)]     # Regula que el productor tenga hueco para producir (el empty)
    mutex = Lock()                                                      # Regula el acceso a la lista de productos producidos (solo puede haber una persona editandola al mismo tiempo)


    # Creo un proceso por cada productor
    procesosProductores = [ Process(target=producer,
                                    name=f'Productor_{i}',
                                    args=(listaProducidos, lSemPuedeProducir, lSemPuedeConsumir, mutex,indicesProducir))
                            for i in range(NPROD) ]


    # Creo el proceso pedido "merge", siendo este la accion del consumidor
    merge = Process(target=consumer,
                    args=(listaProducidos, lSemPuedeProducir, lSemPuedeConsumir, mutex, listaConsumidos, contadorConsumidos, indicesConsumir))


    # Puesta en marcha de los procesos creados
    for p in procesosProductores:
        p.start()
    
    merge.start()

    for p in procesosProductores:
        p.join()

    merge.join()

    # Resultados obtenidos:
    print ("\nUltima produccioón: ")
    for i in range(NPROD):
        print(f"Buffer final del productor {i}: {listaProducidos[i][:]}")

    print ("\nProductos vendidos: ", listaConsumidos[:])

if __name__ == '__main__':
    main()
