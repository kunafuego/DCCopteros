from funcion_parametros import buscar_parametros as p
from PyQt5.QtCore import QThread
import json
from time import sleep
from collections import deque


class ThreadTurno(QThread):

    def __init__(self, senal, senal_segundos):
        super().__init__()                                                                                                                                               
        self.senal_enviar_turno = senal
        self.senal_bajar_segundos = senal_segundos
        #self.senal_cambiar_tiempo = senal_tiempo
        self.conectado = True

    def run(self):
        tiempo_a_esperar = p("tiempo_turno")
        while self.conectado:
            for i in range(1, tiempo_a_esperar):
                sleep(1)
                mensaje = {
                    "comando": "setear_tiempo_turno",
                    "segundos": tiempo_a_esperar - i
                }
                self.senal_bajar_segundos.emit(mensaje)
                if not self.conectado:
                    break
            if self.conectado:
                self.senal_enviar_turno.emit()
            sleep(1)

    def stop(self):
        self.conectado = False
        self.quit()


class Facultad:

    def __init__(self, letra, pos_x, pos_y):
        self.letra = letra
        self.pos_x = pos_x
        self.pos_y = pos_y

    def __repr__(self):
        return self.letra

class Nodo:

    def __init__(self, valor):
        self.valor = valor

    def __repr__(self):
        return repr(self.valor)

class Grafo:
    #La lista de adyacencia tendrá la forma:
    #Nodo: [[nodo_conectado, costo, puntaje que otorga, id dueño del nodo]]
    def __init__(self, lista_adyacencia=None):
        self.lista_adyacencia = lista_adyacencia or dict()

    def adyacentes(self, x, y):
        for lista in self.lista_adyacencia[x]:
            if lista[0] == y:
                return True
        return False


    def revisar_dueño(self, facultad_1, facultad_2):
        #Recibirá dos strings, y debe devolver el dueño
        nodo = [nodo for nodo in self.lista_adyacencia.keys() if str(nodo) == facultad_1][0]
        for lista in self.lista_adyacencia[nodo]:
            if str(lista[0]) == facultad_2:
                return lista[3]
        raise TypeError

    def revisar_baterias(self, facultad_1, facultad_2):
        #Recibirá dos strings con los nombres de las facultades, debe devolver las baterías
        nodo = [nodo for nodo in self.lista_adyacencia.keys() if str(nodo) == facultad_1][0]
        for lista in self.lista_adyacencia[nodo]:
            if str(lista[0]) == facultad_2:
                return lista[1]

    def comprar_camino(self, facultad_1, facultad_2, id_cliente):
        #print(f"Comprando camino entre {facultad_1} y {facultad_2}")
        nodo_1 = [nodo for nodo in self.lista_adyacencia.keys() if str(nodo) == facultad_1][0]
        nodo_2 = [nodo for nodo in self.lista_adyacencia.keys() if str(nodo) == facultad_2][0]
        for lista in self.lista_adyacencia[nodo_1]:
            if lista[0] == nodo_2:
                #Recogemos la lista de la conexión entre ambos nodos
                lista_agregada = lista
                #Actualizamos el dueño
                lista_agregada[3] = id_cliente
                #Agarramos la lista de listas
                lista_cambio = self.lista_adyacencia[nodo_1]
                #Le borramos la lista de ahora
                lista_cambio.remove(lista)
                #Le agregamos la lista cambiada
                lista_cambio.append(lista_agregada)
                #Cambiamos el atributo
                self.lista_adyacencia[nodo_1] = lista_cambio
        for lista in self.lista_adyacencia[nodo_2]:
            if lista[0] == nodo_1:
                baterias_compra = lista[1]
                puntaje = lista[2]
                #Recogemos la lista de la conexión entre ambos nodos
                lista_agregada = lista
                #Actualizamos el dueño
                lista_agregada[3] = id_cliente
                #Agarramos la lista de listas
                lista_cambio = self.lista_adyacencia[nodo_2]
                #Le borramos la lista de ahora
                lista_cambio.remove(lista)
                #Le agregamos la lista cambiada
                lista_cambio.append(lista_agregada)
                #Cambiamos el atributo
                self.lista_adyacencia[nodo_2] = lista_cambio
        #print(f"La compra fue completada, la nueva lista es {self.lista_adyacencia}")
        return baterias_compra, puntaje
        #Como solo se compra un camino en cada vez que se llama la función, no hay problema
        #en cambiar la lista en la que se está iterando

    def __repr__(self):
        texto_nodos = []
        for nodo, vecinos in self.lista_adyacencia.items():
            texto_nodos.append(f"Conexiones de {nodo}: {vecinos}.")
        return "\n".join(texto_nodos)

    def diccionario(self):
        return self.lista_adyacencia

    def actualizar_ruta_larga(self, id):
        """
        Jamás pensé que esta parte me iba a tomar tanto problema :), pero la pude lograr adaptando
        un código (link en el README)
        """
        #Primero buscamos todos los nodos que tengan alguna conexión de id
        nodos = []
        for nodo in self.lista_adyacencia.keys():
            for lista in self.lista_adyacencia[nodo]:
                if lista[3] == id and lista[0] not in nodos:
                    nodos.append(lista[0])

        camino_mas_pesado = 0
        for nodo_id in nodos:
            peso = self.camino_mas_pesado(nodo_id, id)
            if peso > camino_mas_pesado:
                camino_mas_pesado = peso
        return camino_mas_pesado
        

    def BFS(self, nodo_incio, id):
        # marking all nodes as unvisited
        visited = {k: False for k in self.lista_adyacencia.keys()}
        # mark all distance with -1
        distance = {k: -1 for k in self.lista_adyacencia.keys()}
 
        # distance of u from u will be 0
        distance[nodo_incio] = 0
        # in-built library for queue which performs fast operations on both the ends
        queue = deque()
        queue.append(nodo_incio)
        # mark node u as visited
        visited[nodo_incio] = True
 
        while queue:
 
            # pop the front of the queue(0th element)
            nodo = queue.popleft()
            # loop for all adjacent nodes of node front
 
            for lista in self.lista_adyacencia[nodo]:
                if not visited[lista[0]] and lista[3] == id:
                    # mark the ith node as visited
                    visited[lista[0]] = True
                    # make distance of i , one more than distance of front
                    distance[lista[0]] = distance[nodo] + lista[1]
                    # Push node into the stack only if it is not visited already
                    queue.append(lista[0])
 
        maxDis = 0
 
        # get farthest node distance and its index
        for nodo in self.lista_adyacencia:
            if distance[nodo] > maxDis:
                maxDis = distance[nodo]
                nodeIdx = nodo
 
        return nodeIdx, maxDis
 
    # method prints longest path of given tree
    def camino_mas_pesado(self, nodo_inicio, id):
 
        # first DFS to find one end point of longest path
        node, Dis = self.BFS(nodo_inicio, id)
 
        # second DFS to find the actual longest path
        node_2, LongDis = self.BFS(node, id)
 
        return LongDis

    def revisar_cumplio_objetivo(self, objetivo, id):
        """
        Esta función debe recorrer todos los caminos posibles y chequear si es que las facultades 
        están conectadas de alguna forma o no mediante DFS
        retorna un booleano
        """
        facultad_1, facultad_2 = objetivo
        nodo_1 = [nodo for nodo in self.lista_adyacencia.keys() if str(nodo) == facultad_1][0]
        nodo_2 = [nodo for nodo in self.lista_adyacencia.keys() if str(nodo) == facultad_2][0]
        # Vamos a mantener un set con los nodos visitados.
        visitados = set()

        # El stack de siempre, comienza desde el nodo inicio.
        stack = [nodo_1]

        while len(stack) > 0:
            vertice = stack.pop()
            # Detalle clave: si ya visitamos el nodo, ¡no hacemos nada!

            # Lo visitamos
            visitados.add(vertice)

            # Agregamos los vecinos al stack si es que no han sido visitados.
            for vecino in self.lista_adyacencia[vertice]:
                if vecino[0] not in visitados and vecino[3] == id:
                    if nodo_2 == vecino[0]:
                        return True
                    stack.append(vecino[0])
        #print("No están conectados")
        return False

def generar_lista_adyacencia(nombre_mapa, mapa_auxilio=None):
    #nombre_mapa debe ser san_joaquin o ingenieria
    #Devuelve una lista de adyacencia con nodos
    mapa = dict()
    diccionario_nodos = dict()
    with open("mapa.json", encoding="utf-8") as archivo:
        diccionario_completo = json.load(archivo)
        mapa = diccionario_completo["mapa"][nombre_mapa]
        for nodo in mapa["posiciones"].items():
            nombre = nodo[0]
            pos_x = nodo[1]["x"]
            pos_y = nodo[1]["y"]
            nodo_creado = Nodo(Facultad(nombre, pos_x, pos_y))
            diccionario_nodos[nombre] = nodo_creado
        lista_adyacencia_letras = mapa["caminos"]
        lista_adyacencia_nodos = dict()
        for nodo_conexiones in lista_adyacencia_letras.items():
            letra_llave = nodo_conexiones[0]
            conexiones = nodo_conexiones[1]
            #conexiones es una lista de listas, siendo cada lista de la forma [letra, valor]
            nodo_llave = diccionario_nodos[letra_llave]
            lista_conexiones = list()
            for letra, valor in conexiones:
                nodo_letra = diccionario_nodos[letra]
                puntaje = valor
                if valor == 3:
                    puntaje = 4
                elif valor == 4:
                    puntaje = 7
                elif valor == 5:
                    puntaje = 10
                elif valor == 6:
                    puntaje = 15
                elif valor == 7:
                    puntaje = 20
                lista = [nodo_letra, valor, puntaje, "NADIE"]
                if mapa_auxilio is not None:
                    nodo_1 = str(nodo_llave)
                    nodo_2 = str(nodo_letra)
                    for lista_conexion in mapa_auxilio[nodo_1]:
                        if lista_conexion[0] == nodo_2:
                            if lista_conexion[3] != "NADIE":
                                lista[3] = lista_conexion[3]
                lista_conexiones.append(lista)
            lista_adyacencia_nodos[nodo_llave] = lista_conexiones
        return lista_adyacencia_nodos

