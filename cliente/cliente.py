"""
Modulo contiene implementación principal del cliente
"""
from funcion_parametros import buscar_parametros as p
from interfaz import Controlador
from codificacion import (codificar_mensaje, decodificar_mensaje, decodificar_imagen)
import threading
import socket


class Cliente:

    def __init__(self):
        self.host = p("host")
        self.port = p("port")
        #self.log_activado = log_activado
        self.controlador = Controlador(self)
        # Crear socket IPv4, TCP
        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.iniciar_cliente()

    def iniciar_cliente(self):
        try:
            self.socket_cliente.connect((self.host, self.port))
            self.conectado = True
            thread = threading.Thread(target=self.escuchar_servidor)
            thread.start()
            self.controlador.mostrar_inicio()
        except ConnectionResetError:
            self.socket_cliente.close()

    def escuchar_servidor(self):
        try:
            while self.conectado:
                mensaje = self.recibir()
                if not mensaje:
                    raise ConnectionResetError
                self.controlador.manejar_mensaje(mensaje)
        except ConnectionResetError:
            pass
        finally:
            self.socket_cliente.close()
        
        """Ciclo principal que escucha al servidor.

        Recibe mensajes desde el servidor, y genera una respuesta adecuada.
        """
    
    def recibir(self):
        bytes_mensaje = bytearray()
        bytes_largo_mensaje = self.socket_cliente.recv(4)
        largo_mensaje = int.from_bytes(bytes_largo_mensaje, byteorder="big")
        bytes_tipo_mensaje = self.socket_cliente.recv(4)
        tipo_mensaje = int.from_bytes(bytes_tipo_mensaje, byteorder="little")
        if tipo_mensaje == 1:
            numero_bytes_bloques = 4 * ((largo_mensaje // p("chunk_size_imagenes")) + 1)
            largo_mensaje += numero_bytes_bloques
            bytes_color_imagen = self.socket_cliente.recv(4)
            color_imagen = int.from_bytes(bytes_color_imagen, byteorder="big")
            while len(bytes_mensaje) < largo_mensaje:
                bytes_mensaje += self.socket_cliente.recv(min(4096, 
                                                            largo_mensaje - len(bytes_mensaje)))
            while (len(bytes_mensaje) - numero_bytes_bloques) % p("chunk_size_imagenes") != 0:
                #Recibo los 0 que faltan
                bytes_mensaje += self.socket_cliente.recv(1)
            mensaje_decodificado = decodificar_imagen(bytes_largo_mensaje + bytes_tipo_mensaje + 
                                                        bytes_color_imagen + bytes_mensaje)
        elif tipo_mensaje == 2:
            numero_bytes_bloques = 4 * ((largo_mensaje // p("chunk_size_mensajes")) + 1)
            largo_mensaje += numero_bytes_bloques
            while len(bytes_mensaje) < largo_mensaje:
                bytes_a_recibir = min(4096, largo_mensaje - len(bytes_mensaje))
                bytes_mensaje += self.socket_cliente.recv(bytes_a_recibir)
            while (len(bytes_mensaje) - numero_bytes_bloques) % p("chunk_size_mensajes") != 0:
                #Recibo los 0 que faltan
                bytes_mensaje += self.socket_cliente.recv(1)
            bytes_totales = bytes_largo_mensaje + bytes_tipo_mensaje + bytes_mensaje
            mensaje_decodificado = decodificar_mensaje(bytes_totales)
        return mensaje_decodificado

    def enviar(self, mensaje):
        """Envía un mensaje a un cliente.

        Argumentos:
            mensaje (dict): Contiene la información a enviar.
        """
        try:
            mensaje_codificado = codificar_mensaje(mensaje)
            self.socket_cliente.sendall(mensaje_codificado)
        except ConnectionError:
            self.socket_cliente.close()