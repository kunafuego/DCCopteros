"""
Este módulo contiene la clase Logica
"""
import json
from random import choice, choices
from threading import Lock
from funcion_parametros import buscar_parametros as p


class Logica:

    ingreso_lock = Lock()
    usuarios_activos_lock = Lock()

    def __init__(self):

        self.usuarios_activos = dict()
        self.usuarios_partida = dict()
        

    def manejar_mensaje(self, mensaje, id_cliente):
        """
        Maneja un mensaje recibido desde el cliente.
        """
        try:
            comando = mensaje["comando"]
        except KeyError:
            print(f"ERROR: mensaje de cliente {id_cliente} no cumple el formato.")
            return dict()
        respuesta = dict()
        destinatarios = list()
        destinatarios.append(id_cliente)
        if comando == "ingreso":
            nombre_usuario = mensaje["nombre_usuario"]
            print(f"Un jugador ha ingresado el nombre {nombre_usuario},", end="")
            with self.ingreso_lock:
                if len(self.usuarios_activos) == p("cantidad_jugadores_partida"):
                    respuesta = {
                        "comando": "ingreso_rechazado",
                        "comentario": "No hay vacantes disponibles en el juego"
                    }
                    print(" pero hay demasiados usuarios en la partida")
                else:
                    resultado, comentario = self.validar_nombre_usuario(nombre_usuario)
                    if resultado:
                        with self.usuarios_activos_lock:
                            print(" y el nombre ingresado es válido")
                            self.usuarios_activos[id_cliente] = (nombre_usuario, "PENDIENTE", None)
                            destinatarios = [id for id in self.usuarios_activos.keys()]
                            respuesta = {
                            "comando": "ingreso_aceptado",
                            "nombre_usuario": nombre_usuario,
                            "id": id_cliente}
                            if len(self.usuarios_activos) == 1:
                                respuesta["host"] = True
                            else:
                                respuesta["host"] = False
                            respuesta["usuarios"] = self.usuarios_activos
                    else:
                        print(" pero el nombre ingresado no es válido")
                        respuesta = {
                            "comando": "ingreso_rechazado",
                            "comentario": comentario,
                        }
        elif comando == "reingreso":
            nombre_usuario = mensaje["nombre_usuario"]
            with self.ingreso_lock:
                if len(self.usuarios_activos) == p("cantidad_jugadores_partida"):
                    respuesta = {
                        "comando": "reingreso_rechazado",
                        "comentario": "No hay vacantes disponibles en el juego"
                    }
                else:
                    with self.usuarios_activos_lock:
                        self.usuarios_activos[id_cliente] = (nombre_usuario, "PENDIENTE", None)
                        destinatarios = [id for id in self.usuarios_activos.keys()]
                        respuesta = {
                        "comando": "ingreso_aceptado",
                        "nombre_usuario": nombre_usuario,
                        "id": id_cliente}
                        if len(self.usuarios_activos) == 1:
                            respuesta["host"] = True
                        else:
                            respuesta["host"] = False
                        respuesta["usuarios"] = self.usuarios_activos
            pass
        elif comando == "votar":
            nombre_usuario = self.usuarios_activos[id_cliente][0]
            #Guardamos el voto en el diccionario self.votos
            opcion = mensaje["opcion_elegida"]
            #Guardamos este id como listo en la lista de usuarios
            self.usuarios_activos[id_cliente] = (nombre_usuario, "LISTO", opcion)
            #Le enviamos los diccionarios a todos para que actualicen
            destinatarios = [id for id in self.usuarios_activos.keys()]
            print(f"El jugador {nombre_usuario} ya votó, y se encuentra listo para la partida")
            respuesta = {
                "comando": "actualizar_situaciones",
                "usuarios": self.usuarios_activos,
            }
            todos_listos = True
            for usuario in self.usuarios_activos.values():
                if usuario[1] == "PENDIENTE":
                    todos_listos = False
            if todos_listos:
                print("Todos los usuarios se encuentran listos para iniciar la partida")
        elif comando == "jugador_retirado":
            #Mandamos toda la info sin el jugador que sacaron
            destinatarios = [id for id in self.usuarios_activos.keys()]
            respuesta = {
                "comando": "actualizar_situaciones",
                "usuarios": self.usuarios_activos
            }
        elif comando == "comenzar_juego":
            #Debemos decirle a todos los jugadores que partió la partida
            destinatarios = [id for id in self.usuarios_activos.keys()]
            respuesta["comando"] = "comenzar_partida"
            self.usuarios_partida = {key: {"baterias": 0, "puntaje": 0, "ruta_mas_larga": 0} \
                for key in self.usuarios_activos.keys()}
            respuesta["mapa"] = self.elegir_mapa()
            respuesta["turno_actual"] = 1
            #self.usuarios_partida = {"id":{nombre:, foto:, turno:, baterias:, puntaje:, objetivo:
            #, objetivo_cumplido, ruta_mas_larga)
            self.designar_objetivos(respuesta["mapa"])
            self.designar_nombres()
            self.elegir_turnos()
            self.designar_fotos(mensaje["fotos_tomadas"])
            respuesta["usuarios"] = self.usuarios_partida
            nombre_tuno1 = [valor["nombre"] for valor in self.usuarios_partida.values() if \
                                                                            valor["turno"] == 1][0]
            print("Se ha comenzado una nueva partida")
            print(f"Es el turno del cliente con turno 1, que le corresponde a {nombre_tuno1}")
        
        elif comando == "log_compra_fallida":
            nombre = mensaje["nombre_jugador"]
            error = mensaje["mensaje_error"]
            baterias = mensaje["baterias"]
            print(f"El jugador {nombre} ha intentado comprar un camino pero" +
            f" no ha podido porque {error}. De todas maneras al cliente le " + 
            f"quedan {baterias} baterias")
        
        elif comando == "setear_tiempo_turno":
            destinatarios = [id for id in self.usuarios_activos.keys()]
            respuesta = mensaje
        elif comando == "info_turno":
            termino_juego = self.revisar_termino_juego(mensaje["grafo_mapa"])
            if termino_juego:
                #Termima el juego
                #Calculamos los puntajes totales
                self.calcular_puntajes()
                respuesta["comando"] = "termino_juego"
                respuesta["usuarios"] = self.usuarios_partida
                destinatarios = [id for id in self.usuarios_activos.keys()]
                #Termino el juego, por lo que reseteamos los atributos
                self.usuarios_activos = dict()
                self.usuarios_partida = dict()
                ganador = None
                max_puntaje = 0
                for usuario in self.usuarios_partida.values():
                    if usuario["puntaje_final"] > max_puntaje:
                        ganador = usuario["nombre"]
                        max_puntaje = usuario["puntaje_final"]
                print(f"Ha terminado la partida, y ha ganado {ganador}")
            else:
                try:
                    jugada = mensaje["jugada_realizada"]
                    jugador = mensaje["jugador_turno"]
                    if jugada == "sacar carta":
                        baterias = mensaje["cantidad_baterias"]
                        print(f"El jugador {jugador} sacó una carta de {baterias} baterias")
                    elif jugada == "comprar camino":
                        baterias = mensaje["baterias_actuales"]
                        camino = mensaje["camino_comprado"]
                        print(f"El jugador {jugador} ha comprado el camino {camino}, y ahora" +
                        f"ha quedado con {baterias} baterias restantes")
                except KeyError:
                    pass
                turno = mensaje["turno_actual"]
                if turno == p("cantidad_jugadores_partida"):
                    turno_actual = 1
                else:
                    turno_actual = turno + 1
                nombre = [valor["nombre"] for valor in self.usuarios_partida.values() \
                                                                if valor["turno"] == turno_actual]
                print(f"Comienza el turno de un cliente. Es el número {turno_actual}, que",
                    f"le corresponde al jugador {nombre[0]}")
                respuesta = mensaje
                respuesta["comando"] = "nuevo_turno"
                self.usuarios_partida = mensaje["usuarios"]
                respuesta["turno_actual"] = turno_actual
                destinatarios = [id for id in self.usuarios_activos.keys()]
        else:
            print(f"Error: comando {comando} inválido")
        return respuesta, destinatarios        

    def validar_nombre_usuario(self, nombre_usuario):
        """
        Recibe un nombre de usuario, y revisa si este ya está activo (conectado) o no.
        """
        with self.usuarios_activos_lock:
            # Revisar nombre en los usuarios activos
            nombres_usuarios = [nombre[0] for nombre in self.usuarios_activos.values()]
            if nombre_usuario in nombres_usuarios:
                return False, "Este usuario está siendo usado por otro cliente"
            # Revisar nombre en los usuarios registrados
            if len(nombre_usuario) > 15:
                return False, "El nombre de usuario es demasiado largo"
            return True, None

    def revisar_termino_juego(self, grafo):
        termino = True
        for key in grafo.keys():
            lista_de_listas_llave = grafo[key]
            for lista in lista_de_listas_llave:
                """
                if str(key) == "A" and str(lista[0]) == "B" and lista[3] != "NADIE":
                    return True
                """
                if lista[3] == "NADIE":
                    termino = False
                    break
            if not termino:
                break
        return termino

    def calcular_puntajes(self):
        #Al diccionario de usuarios.values() le sumará un par {puntaje_final: punatje}
        #Sacar el id con ruta más larga
        valor_ruta_mas_larga = 0
        for id in self.usuarios_partida.keys():
            valor_ruta_mas_larga_usuario = self.usuarios_partida[id]["ruta_mas_larga"]
            if valor_ruta_mas_larga_usuario > valor_ruta_mas_larga:
                valor_ruta_mas_larga = valor_ruta_mas_larga_usuario
            puntaje = self.usuarios_partida[id]["puntaje"]
            if self.usuarios_partida[id]["objetivo_cumplido"]:
                puntaje += p("puntos_objetivo")
            else:
                puntaje -= p("puntos_objetivo")
            self.usuarios_partida[id]["puntaje_final"] = puntaje
        for id in self.usuarios_partida.keys():
            if self.usuarios_partida[id]["ruta_mas_larga"] == valor_ruta_mas_larga:
                puntaje_sin_bonus = self.usuarios_partida[id]["puntaje_final"]
                puntaje_con_bonus = puntaje_sin_bonus + p("puntos_ruta_larga")
                self.usuarios_partida[id]["puntaje_final"] = puntaje_con_bonus

    def desconectar_usuario(self, id_cliente):
        """
        Recibe una id de un cliente desde el servidor y la saca junto a su usuario asociado
        de el diccionario de usuarios activos.
        """
        with self.usuarios_activos_lock:
            try:

                del self.usuarios_activos[id_cliente]
            except KeyError:
                pass
    def elegir_mapa(self):
        votos_ing = [1 for usuario in self.usuarios_activos.values() if \
                                                            usuario[2] == "mapa_ingenieria"]
        votos_sanjoaquin = [1 for usuario in self.usuarios_activos.values() if \
                                                            usuario[2] == "mapa_sanjoaquin"]
        if len(votos_ing) > len(votos_sanjoaquin):
            return "mapa_ingenieria"
        elif len(votos_ing) < len(votos_sanjoaquin):
            return "mapa_sanjoaquin"
        return choice(["mapa_ingenieria", "mapa_sanjoaquin"])

    def elegir_turnos(self):
        turnos_disponibles = [num for num in range(1, 1 + p("cantidad_jugadores_partida"))]
        for id in self.usuarios_partida.keys():
            turno_elegido = choice(turnos_disponibles)
            turnos_disponibles.remove(turno_elegido)
            self.usuarios_partida[id]["turno"] = turno_elegido

    def designar_fotos(self, fotos_tomadas):
        for id in self.usuarios_partida.keys():
            nombre = self.usuarios_partida[id]["nombre"]
            foto_id = [foto[1] for foto in fotos_tomadas if foto[0] == id]
            if foto_id[0] == p("foto_1"):
                print(f"El usuario {nombre} tiene el avatar de color azul")
                self.usuarios_partida[id]["color_foto"] = 1
            if foto_id[0] == p("foto_2"):
                print(f"El usuario {nombre} tiene el avatar de color rojo")
                self.usuarios_partida[id]["color_foto"] = 2
            if foto_id[0] == p("foto_3"):
                print(f"El usuario {nombre} tiene el avatar de color verde")
                self.usuarios_partida[id]["color_foto"] = 3
            if foto_id[0] == p("foto_4"):
                print(f"El usuario {nombre} tiene el avatar de color amarillo")
                self.usuarios_partida[id]["color_foto"] = 4

    def designar_nombres(self):
        for id in self.usuarios_partida.keys():
            nombre_id = [valor[0] for valor in self.usuarios_activos.values() if \
                self.usuarios_activos[id] == valor]
            self.usuarios_partida[id]["nombre"] = nombre_id[0]
    
    def designar_objetivos(self, nombre_mapa):
        if nombre_mapa == "mapa_ingenieria":
            nombre_mapa = "ingenieria"
        else:
            nombre_mapa = "san_joaquin"
        with open("mapa.json", encoding="utf-8") as archivo:
            diccionario_completo = json.load(archivo)
            mapa = diccionario_completo["mapa"][nombre_mapa]
        numero_nodos = mapa["numero_nodos"]
        facultades = [chr(i) for i in range(65, 65 + numero_nodos)]
        for id in self.usuarios_partida.keys():
            while True:
                #Código de intro :( pero no me queda más cabeza jaja
                m = 0
                facultad_1, facultad_2 = tuple(choices(facultades, k=2))
                lista_caminos_1 = mapa["caminos"][facultad_1]
                for lista in lista_caminos_1:
                    if lista[0] == facultad_2:
                        m = 1
                if facultad_2 == facultad_1:
                    m = 1
                if m == 0:
                    break
            self.usuarios_partida[id]["objetivo"] = (facultad_1, facultad_2)
            self.usuarios_partida[id]["objetivo_cumplido"] = False

            
                