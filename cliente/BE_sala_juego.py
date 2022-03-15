from funcion_parametros import buscar_parametros as p
from PyQt5.QtCore import QObject, pyqtSignal
from clasesBE import ThreadTurno, Grafo, generar_lista_adyacencia
from random import randint


class BESalaJuego(QObject):

    senal_enviar_info_comienzo = pyqtSignal(dict)
    senal_enviar_turno_server = pyqtSignal(dict)
    senal_enviar_info_turno = pyqtSignal(dict)
    senal_aviso_camino = pyqtSignal(str)
    senal_enviar_turno_thread = pyqtSignal()
    senal_enviar_log_camino = pyqtSignal(dict)
    senal_enviar_segundos = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.id = 0
        self.nombre_usuario = None
        self.info_jugador = dict()
        self.info_otros_jugadores = dict()
        self.turno_actual = 0
        self.jugador_turno = None
        self.mapa = None
        self.color_foto = None
        self.fotos = list()
        self.grafo_mapa = dict()
        self.objetivo = None
        self.thread_turno = None
        self.senal_enviar_turno_thread.connect(self.enviar_turno)

    def info_comienzo_partida(self, mensaje):
        self.id = mensaje["id"]
        if mensaje["mapa"] == "mapa_ingenieria":
            self.mapa = "ingenieria"
        elif mensaje["mapa"] == "mapa_sanjoaquin":
            self.mapa = "san_joaquin"
        self.color_foto = mensaje["color_foto_usuario"]
        self.info_fotos = mensaje["info_fotos"]
        self.nombre_usuario = mensaje["nombre_usuario"]
        self.usuarios = mensaje["usuarios"]
        for id in self.usuarios.keys():
            color_foto = self.usuarios[id]["color_foto"]
            for foto in self.info_fotos:
                if foto[1] == color_foto:
                    self.usuarios[id]["bytes_foto"] = foto[0]

        self.turno_actual = mensaje["turno_actual"]
        self.jugador_actual = [dic["nombre"] for dic in self.usuarios.values() if \
                                                        int(dic["turno"]) == self.turno_actual][0]
        mensaje["jugador_actual"] = self.jugador_actual
        self.objetivo = self.usuarios[self.id]["objetivo"]
        #Guardamos un diccionario con la info del jugador
        self.info_jugador = mensaje["usuarios"][mensaje["id"]]
        #Guardamos otro diccionario con la info de los otros jugadores
        self.info_otros_jugadores = {k: v for k, v in self.usuarios.items() if k != self.id}
        mensaje["info_jugador"] = self.info_jugador
        mensaje["info_otros_jugadores"] = self.info_otros_jugadores
        #Después de cambiar muchos atributos:
        self.grafo_mapa = Grafo(generar_lista_adyacencia(self.mapa))
        #Generamos thread para el primer turno
        if self.nombre_usuario == self.jugador_actual:
            pass
            self.generar_thread_turno()
        self.senal_enviar_info_comienzo.emit(mensaje)

    def sacar_carta(self):
        #Esta función le agrega una cantidad de baterías random al jugador y envía el turno
        #al servidor
        numero_baterias = randint(p("baterias_min"), p("baterias_max"))
        nuevas_baterias = self.usuarios[self.id]["baterias"] + numero_baterias
        self.usuarios[self.id]["baterias"] = nuevas_baterias
        mensaje = {
            "jugada_realizada": "sacar carta",
            "baterias": numero_baterias,
            "jugador_turno": self.nombre_usuario
        }
        self.enviar_turno(mensaje)
        
    def senal_enviar_camino_fallido(self, mensaje):
        diccionario_turno = {
            "comando": "log_compra_fallida",
            "mensaje_error": mensaje,
            "nombre_jugador": self.nombre_usuario,
            "baterias": self.usuarios[self.id]["baterias"]
        }
        self.senal_enviar_log_camino.emit(diccionario_turno)    

    def comprar_camino(self, tupla_camino):
        #Esta función revisa si se puede comprar el camino que el jugador indicó.
        #De ser así, lo compra mediante un método de la clase grafo
        facultad_1, facultad_2 = tupla_camino
        if len(facultad_1) != 1 or len(facultad_2) != 1 or not facultad_1.isalpha() or \
            not facultad_2.isalpha():
            self.senal_aviso_camino.emit("Debes ingresar valores válidos")
            self.senal_enviar_camino_fallido("Debes ingresar valores válidos")
            return None
        list_nodo_facultad_1 = [nodo for nodo in self.grafo_mapa.lista_adyacencia.keys() if \
                                                                    str(nodo) == facultad_1]
        list_nodo_facultad_2 = [nodo for nodo in self.grafo_mapa.lista_adyacencia.keys() if \
                                                                    str(nodo) == facultad_2]
        try:
            nodo_facultad_1 = list_nodo_facultad_1[0]
            nodo_facultad_2 = list_nodo_facultad_2[0]
        except IndexError:
            self.senal_enviar_camino_fallido("Debes ingresar valores válidos")
            self.senal_aviso_camino.emit("Debes ingresar valores válidos")
            return None
        adyacencia = self.grafo_mapa.adyacentes(nodo_facultad_1, nodo_facultad_2) 
        if not adyacencia:
            aviso = "Las facultades seleccionadas no son adyacentes"
            self.senal_enviar_camino_fallido(aviso)
            self.senal_aviso_camino.emit(aviso)
            return None
        owner = self.grafo_mapa.revisar_dueño(facultad_1, facultad_2)
        if owner != "NADIE":
            aviso = "El camino ya es propiedad de otro jugador"
            self.senal_enviar_camino_fallido(aviso)
            self.senal_aviso_camino.emit(aviso)
            return None
            #Emitimos señal de que ya está comprado
        baterias = self.grafo_mapa.revisar_baterias(facultad_1, facultad_2)
        if baterias > self.info_jugador["baterias"]:
            aviso = "No tienes suficientes baterías para comprar este camino"
            self.senal_enviar_camino_fallido(aviso)
            self.senal_aviso_camino.emit(aviso)
            return None
        #Función que efectúa la compra del mapa y devuelve las baterías y el puntaje
        #print('Estaba todo ok, procederemos a comprar el camino')
        baterias_compra, puntaje = self.grafo_mapa.comprar_camino(facultad_1, facultad_2, self.id)
        #print("Camino comprado, enviaremos el turno")
        self.usuarios[self.id]["baterias"] -= baterias_compra
        self.usuarios[self.id]["puntaje"] += puntaje
        mensaje = {
            "baterias_actuales": self.usuarios[self.id]["baterias"],
            "camino_comprado": str(str(facultad_1) + "-" + str(facultad_2)),
            "jugada_realizada": "comprar camino",
            "jugador_turno": self.nombre_usuario
        }
        self.objetivo_listo = self.grafo_mapa.revisar_cumplio_objetivo(self.objetivo, self.id)
        self.usuarios[self.id]["objetivo_cumplido"] = self.objetivo_listo
        self.usuarios[self.id]["ruta_mas_larga"] = self.grafo_mapa.actualizar_ruta_larga(self.id)
        self.enviar_turno(mensaje)

    def enviar_turno(self, mensaje=None):
        """
        Esta función es llamada cuando el turno ya está listo.
        Arma un diccionario y se lo envía al servidor
        """
        #Si no fue llamado por el thread lo detenemos
        if self.thread_turno.isRunning():
            self.thread_turno.stop()
        else:
            self.thread_turno.stop()
        mensaje_turno = dict()
        if mensaje:
            mensaje_turno["jugada_realizada"] = mensaje["jugada_realizada"]
            mensaje_turno["jugador_turno"] = mensaje["jugador_turno"]
            if mensaje["jugada_realizada"] == "sacar carta":
                mensaje_turno["cantidad_baterias"] = mensaje["baterias"]
            elif mensaje["jugada_realizada"] == "comprar camino":
                mensaje_turno["baterias_actuales"] = mensaje["baterias_actuales"]
                mensaje_turno["camino_comprado"] = mensaje["camino_comprado"]
                pass
        mensaje_turno["comando"] = "info_turno"
        mensaje_turno["usuarios"] = self.usuarios
        mensaje_turno["grafo_mapa"] = self.convertir_grafo_a_str(self.grafo_mapa)
        mensaje_turno["turno_actual"] = self.turno_actual
        self.senal_enviar_turno_server.emit(mensaje_turno)
        pass
    
    def nuevo_turno(self, mensaje):
        """
        Esta función recibe la información de un nuevo turno,
        actualiza el backend y luego el FE
        """
        #Guardamos la info de todos los usuarios
        self.usuarios = mensaje["usuarios"]
        #Guardamos un diccionario con la info del jugador
        self.info_jugador = mensaje["usuarios"][self.id]
        #Metemos en el mensaje los diccionarios más específicos para facilitar el trabajo del FE
        mensaje["info_jugador"] = self.info_jugador
        #Guardamos un dict con la info de los otros jugadores y lo metemos al mensaje
        self.info_otros_jugadores = {k: v for k, v in self.usuarios.items() if k != self.id}
        mensaje["info_otros_jugadores"] = self.info_otros_jugadores
        self.turno_actual = mensaje["turno_actual"]
        self.jugador_actual = [dic["nombre"] for dic in self.usuarios.values() if \
                                                    int(dic["turno"]) == self.turno_actual][0]
        mensaje["jugador_actual"] = self.jugador_actual
        self.grafo_mapa = Grafo(generar_lista_adyacencia(self.mapa, \
                                                            mapa_auxilio=mensaje["grafo_mapa"]))
        lineas = self.formar_lineas_mapa()
        if len(lineas) != 0:
            mensaje["lineas"] = lineas
        if self.nombre_usuario == self.jugador_actual:
            self.generar_thread_turno()
            pass
        self.senal_enviar_info_turno.emit(mensaje)

    def generar_thread_turno(self):
        thread_turno = ThreadTurno(self.senal_enviar_turno_thread, self.senal_enviar_segundos)
        thread_turno.start()
        self.thread_turno = thread_turno

    
    def formar_lineas_mapa(self):
        """
        Esta función debe devolver de adonde a adonde irá cada línea, y de qué color será
        lineas = [[color, (x1, y1), (x2, y2)], [...]]
        """
        #print("Formando las lineas del mapa")
        lineas = list()
        an_map = p("ancho_mapa")
        al_map = p("alto_mapa")
        lista_adyacencia = self.grafo_mapa.diccionario()
#        print(f"La lsita de adyacencia de la wea  de las lineas es {lista_adyacencia}")
        for nodo_conexiones in lista_adyacencia.items():
            nodo_1 = nodo_conexiones[0]
            listas_conexiones = nodo_conexiones[1]
#            print(f"Sus listas de conexiones son {listas_conexiones}")
            for lista in listas_conexiones:
                if lista[3] != "NADIE":
                    #print(f"La lista {lista} tiene dueño")
                    nodo_2 = lista[0]
                    id = lista[3]
                    color_linea = self.usuarios[id]["color_foto"]
                    #print(f"El id es {id}, de color {color_linea}")                                       
                    if self.mapa == "san_joaquin":
                        punto_1 = (an_map * nodo_1.valor.pos_x * 0.92, al_map * nodo_1.valor.pos_y)
                        punto_2 = (an_map * nodo_2.valor.pos_x * 0.92, al_map * nodo_2.valor.pos_y)
                        #hacemos una corrección, pues las líneas en este mapa aparecían corridas
                    else:
                        punto_1 = (an_map * nodo_1.valor.pos_x, al_map * nodo_1.valor.pos_y)
                        punto_2 = (an_map * nodo_2.valor.pos_x, al_map * nodo_2.valor.pos_y)
                    #print(f"Los puntos son {punto_1}, {punto_2}")
                    linea = [color_linea, punto_1, punto_2]
                    #print("Agregamos la línea", linea)
                    lineas.append(linea)
        #print(f"Lista las lineas {lineas}")
        return lineas

    def convertir_grafo_a_str(self, grafo):
        """
        Para enviar mi grafo, convierto todos los nodos a sus strings.
        Si es que lo enviaba a través de pickle, me levantaba un error porque
        el servidor no conocía la clase
        """
        lista_adyacencia_grafo = grafo.diccionario()
        #Ocuparemos este método para poder enviar el grafo al server sin que nos levante error
        diccionario_grafo = dict()
        for nodo_conexiones in lista_adyacencia_grafo.items():
            nodo_1 = str(nodo_conexiones[0])
            lista_conexiones = nodo_conexiones[1]
            conexiones_nodo_1 = list()
            for lista in lista_conexiones:
                nodo_2 = str(lista[0])
                lista_nodo_1_nodo_2 = [nodo_2, lista[1], lista[2], lista[3]]
                conexiones_nodo_1.append(lista_nodo_1_nodo_2)
            diccionario_grafo[nodo_1] = conexiones_nodo_1
        return diccionario_grafo


if __name__ == "__main__":
    grafo = Grafo(generar_lista_adyacencia("ingenieria"))
    be = BESalaJuego()
    be.id = 20
    be.info_jugador = {"baterias": 100}
    be.usuarios = {20: {"baterias": 100, "puntaje": 0}}
    be.grafo_mapa = grafo
    be.objetivo = ("A", "D")
    be.comprar_camino(("A", "B"))
    be.comprar_camino(("A", "C"))
    be.comprar_camino(("C", "D"))
    print(be.grafo_mapa.actualizar_ruta_larga(be.id))