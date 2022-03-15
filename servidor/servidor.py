"""
Modulo contiene implementación principal del servidor
"""
from random import choice
from logica import Logica
import socket
import threading
from funcion_parametros import buscar_parametros as p
from codificacion import (codificar_mensaje, codificar_imagen, decodificar_mensaje)

class Servidor:
    """
    Clase Servidor: Administra la conexión y la comunicación con los clientes

    Atributos:
        host: string que representa la dirección del host (como una URL o una IP address).
        port: int que representa el número de puerto en el cual el servidor recibirá conexiones.
        log_activado: booleano, controla si el programa "printea" en la consola (ver método log).
        socket_servidor: socket del servidor, encargado de recibir conexiones.
        clientes_conectados: diccionario que mantiene los sockets de los clientes actualmente
            conectados, de la forma { id : socket_cliente }.
        logica: instancia de Lógica que maneja el funcionamiento interno del programa
    """

    _id_cliente = 0
    # Administra el acceso a clientes_conectados para evitar que se produzcan errores.
    clientes_conectados_lock = threading.Lock()
    recibir_bytes_lock = threading.Lock()

    def __init__(self):
        self.host = p("host")
        self.port = p("port")
        self.socket_servidor = None
        self.iniciar_servidor()
        self.clientes_conectados = {}
        self.fotos_totales = [p("foto_1"), p("foto_2"), p("foto_3"), p("foto_4")]
        self.fotos_disponibles = [p("foto_1"), p("foto_2"), p("foto_3"), p("foto_4")]
        #Lista de tuplas que indica qué id tiene cada foto, para ponerla denuevo cuando se elimine
        self.foto_tomada = list()
        self.threads = list()
        self.logica = Logica()

        # Crea y comienza thread encargado de aceptar clientes
        thread = threading.Thread(target=self.aceptar_clientes, daemon=True)
        thread.start()

    def iniciar_servidor(self):
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Deja unido el puerto con el host, declara que ese es el puerto en el que quiere conexiones
        self.socket_servidor.bind((self.host, self.port))
        self.socket_servidor.listen()

    def aceptar_clientes(self):
        while True:
            socket_cliente, address = self.socket_servidor.accept()
            with self.clientes_conectados_lock:
                print(f"Un nuevo cliente con dirección {address} ha sido aceptado")
                id_cliente = self._id_cliente
                self.clientes_conectados[id_cliente] = socket_cliente
                self._id_cliente += 1
                thread_cliente = threading.Thread(target=self.escuchar_cliente, args=(id_cliente,))
                thread_cliente.start()
                self.threads.append((id_cliente, thread_cliente))

    def escuchar_cliente(self, id_cliente):
        try:
            socket_cliente_id = self.clientes_conectados[id_cliente]
            #Para comenzar le mandamos la foto
            self.enviar_foto(id_cliente, socket_cliente_id)
            while True:
                mensaje = self.recibir(socket_cliente_id)
                #print(f"Recibí este mensaje {mensaje}")
                if mensaje["comando"] == "comenzar_juego":
                    mensaje["fotos_tomadas"] = self.foto_tomada
                if not mensaje:
                    raise ConnectionResetError
                respuesta, destinatarios = self.logica.manejar_mensaje(mensaje, id_cliente)
                if respuesta:
                    for destinatario in destinatarios:
                        socket_cliente = self.clientes_conectados[destinatario]
                        self.enviar(respuesta, socket_cliente)
        except ConnectionResetError:
            print(f"ERROR: conexión con cliente {id_cliente} fue reseteada")            
        self.eliminar_cliente(id_cliente)
    
    def recibir(self, socket_cliente):
        id = [id[0] for id in self.clientes_conectados.items() if id[1] == socket_cliente]
        # Recibir largo del mensaje
        #Solo va a entrar a recv si es que le llega algo
        bytes_largo_mensaje = socket_cliente.recv(4)
        # Decodificar largo del mensaje
        largo_mensaje = int.from_bytes(bytes_largo_mensaje, byteorder="big")
        #Le debo sumar los bloques de al principio de cada chunk
        numero_bytes_bloques = 4 * ((largo_mensaje // p("chunk_size_mensajes")) + 1)
        largo_mensaje += numero_bytes_bloques
        bytes_inutiles = socket_cliente.recv(4)  #Son los 4 bytes del tipo, que no los necesitamos
        bytes_mensaje = bytearray()
        while len(bytes_mensaje) < largo_mensaje:
            bytes_a_recibir = min(4096, largo_mensaje - len(bytes_mensaje))
            bytes_mensaje += socket_cliente.recv(bytes_a_recibir)
        while (len(bytes_mensaje) - numero_bytes_bloques) % p("chunk_size_mensajes") != 0:
            #Recibo los 0 que faltan
            bytes_mensaje += socket_cliente.recv(1)
        bytes_totales = bytes_largo_mensaje + bytes_inutiles + bytes_mensaje
        mensaje_decodificado = decodificar_mensaje(bytes_totales)
        return mensaje_decodificado

    def enviar(self, mensaje, socket_cliente):
        try:
            if mensaje["comando"] == "entrega foto":
                imagen_codificada = codificar_imagen(mensaje["foto"])
                socket_cliente.sendall(imagen_codificada)
            elif mensaje["comando"] == "comenzar_partida":
                self.enviar_todas_las_fotos()
                mensaje_codificado = codificar_mensaje(mensaje)
                socket_cliente.sendall(mensaje_codificado)
            else:
                #print(f"Enviando {mensaje}")
                mensaje_codificado = codificar_mensaje(mensaje)
                socket_cliente.sendall(mensaje_codificado)
                
        except ConnectionError:
            self.socket_cliente.close()


        """Envía un mensaje a un cliente.

        Argumentos:
            mensaje (dict): Contiene la información a enviar.
            socket_cliente (socket): El socket objetivo al cual enviar el mensaje.
        """

    def enviar_todas_las_fotos(self):
        sockets_destinatarios = [socket_id for socket_id in self.clientes_conectados.values()]
        for socket_id in sockets_destinatarios:
            for foto in self.fotos_totales:
                mensaje = {
                    "comando": "entrega foto",
                    "foto": foto
                }
                self.enviar(mensaje, socket_id)


    def eliminar_cliente(self, id_cliente):
        """Elimina un cliente de clientes_conectados.

        Argumentos:
            id_cliente (int): la id del cliente a eliminar del diccionario.
        """
        with self.clientes_conectados_lock:

            #print(f"Borrando socket del cliente {id_cliente}.")
            # Obtener socket
            socket_cliente = self.clientes_conectados[id_cliente]
            # Cerrar socket
            socket_cliente.close()
            # Borrar entrada del diccionario
            del self.clientes_conectados[id_cliente]
            # Borrar usuario de los usuarios activos (Logica)
            self.logica.desconectar_usuario(id_cliente)
            # La foto vuelve a estar disponible
            foto_eliminada = [foto[1] for foto in self.foto_tomada if foto[0] == id_cliente]
            self.foto_tomada = [tupla for tupla in self.foto_tomada if tupla[0] != id_cliente]
            self.fotos_disponibles.append(foto_eliminada[0])

    def cerrar_servidor(self):
        #print("Desconectando clientes...")
        for id_cliente in list(self.clientes_conectados.keys()):
            self.eliminar_cliente(id_cliente)
        #print("Cerrando socket de recepción...")
        self.socket_servidor.close()
    
    def elegir_foto(self):
        foto = choice(self.fotos_disponibles)
        self.fotos_disponibles.remove(foto)
        return foto

    def enviar_foto(self, id_cliente, socket_cliente):
        diccionario_foto = {"comando": "entrega foto", 
                            "foto": self.elegir_foto()}
        self.foto_tomada.append((id_cliente, diccionario_foto["foto"]))
        self.enviar(diccionario_foto, socket_cliente)