from PyQt5.QtCore import pyqtSignal, QObject
from ventanas.ventana_inicio import VentanaInicio
from ventanas.ventana_sala_espera import SalaEspera
from ventanas.ventana_sala_juego import SalaJuego
from ventanas.fin_partida import FinPartida
from BE_sala_juego import BESalaJuego


class Controlador(QObject):
    """
    Clase Controlador: Liga el cliente con la interfaz gráfica. Interpreta los mensajes recibidos
    desde el servidor (manejar_mensaje), aplica los cambios correspondientes en la interfaz, y
    genera la respuesta correspondiente al servidor.
    """
    mostrar_ventana_sala_espera_signal = pyqtSignal(dict)
    mostrar_sala_juego_senal = pyqtSignal(dict)
    senal_fin_partida = pyqtSignal(dict)
    senal_solicitar_reingreso = pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__()
        self.nombre_usuario = None
        self.fotos = list()
        self.es_primera_foto = True
        self.color_foto = None

        self.ventana_inicio = VentanaInicio()
        self.ventana_sala_espera = SalaEspera()
        self.ventana_sala_juego = SalaJuego()

        self.backend_sala_juego = BESalaJuego()

        self.fin_partida = FinPartida()

        #Conectando las señales entre las interfaces y lo que debe enviar el cliente al servidor
        #La primera señal es la de verificar usuario, el cliente debe enviar el diccionario con el 
        #nombre y el servidor debe analizarlo
        self.ventana_inicio.senal_ingreso.connect(parent.enviar)
        #Una vez que fue aceptado, se emite esta señal para que se muestre la ventana de la sala de 
        #espera
        self.mostrar_ventana_sala_espera_signal.connect(self.mostrar_sala_espera)
        #Cada vez que uno de los clientes vote, se lo enviará al servidor
        self.ventana_sala_espera.senal_votar.connect(parent.enviar)
        #Cuando se aprete inicio parte el juego
        self.ventana_sala_espera.senal_comenzar_juego.connect(parent.enviar)
        #Cuando llega la señal de que parta el juego, mostramos la ventana
        #Hago esto con señales porque después de 5 horas, literal 5 horas buscando cómo hacer 
        #aparecer 
        #la ventana no sé por qué esto fue lo único que sirvió
        self.mostrar_sala_juego_senal.connect(self.mostrar_sala_juego)
        #Cuando un jugador haya terminado su turno, le envía la info al server para que la 
        #distribuya y pase al siguiente turno
        self.backend_sala_juego.senal_enviar_turno_server.connect(parent.enviar)
        #Cuando termine la partida, escondemos la ventana de la sala del juego y mostramos 
        #la ventana de fin de partida
        self.senal_fin_partida.connect(self.mostrar_fin)
        #Si quiere volver a jugar, lo mandamos nuevamente a la ventana de sala de espera
        self.fin_partida.senal_volver_a_jugar.connect(self.volver_a_jugar)
        self.senal_solicitar_reingreso.connect(parent.enviar)
        #Cuando un jugador intenta comprar un camino y no puede hay que mandarlo al server para que
        #lo imprima
        self.backend_sala_juego.senal_enviar_log_camino.connect(parent.enviar)
        #Cada vez que baje un segundo debemos enviarlo al server para que le actualice a todos
        self.backend_sala_juego.senal_enviar_segundos.connect(parent.enviar)


        #Señales entre backend y frontend de la partida:
        self.backend_sala_juego.senal_enviar_info_comienzo.connect(self.ventana_sala_juego.\
                                                                            recibir_info_comienzo)
        self.ventana_sala_juego.senal_carta_baterias.connect(self.backend_sala_juego.sacar_carta)
        self.backend_sala_juego.senal_enviar_info_turno.connect(self.ventana_sala_juego.\
                                                                            recibir_info_turno)
        self.ventana_sala_juego.senal_comprar_camino.connect(self.backend_sala_juego.\
                                                                                comprar_camino)
        self.backend_sala_juego.senal_aviso_camino.connect(self.ventana_sala_juego.mostrar_aviso)


    def mostrar_inicio(self):
        self.nombre_usuario = None
        self.host = None
        self.ventana_inicio.show()
    
    def mostrar_sala_espera(self, mensaje):
        self.ventana_inicio.esconder_ventana_inicio()
        self.ventana_sala_espera.actualizar_labels(mensaje)
        self.ventana_sala_espera.mostrar_sala_espera(mensaje)
    
    def mostrar_sala_juego(self, mensaje):
        self.ventana_sala_espera.esconder_sala_espera()
        self.ventana_sala_juego.show()

    def mostrar_fin(self, mensaje):
        self.ventana_sala_juego.esconder_ventana()
        self.fin_partida.mostrar_ventana(mensaje)

    def volver_a_jugar(self):
        mensaje = {"comando": "reingreso",
                    "nombre_usuario": self.nombre_usuario
        }
        self.senal_solicitar_reingreso.emit(mensaje)
    
    def reingreso_rechazado(self, mensaje):
        self.fin_partida.aviso.setText(mensaje["comentario"])

    def manejar_mensaje(self, mensaje):
        """
        Maneja un mensaje recibido desde el servidor.
        Genera la respuesta y los cambios en la interfaz correspondientes.

        Argumentos:
            mensaje (dict): Mensaje ya decodificado recibido desde el servidor
        """
        try:
            comando = mensaje["comando"]
            if comando == "ingreso_aceptado":
                #Si ya está visible la sala de espera solo debemos actualizar los jugadores
                if self.ventana_sala_espera.isVisible():
                    self.ventana_sala_espera.actualizar_labels(mensaje)
                else:
                    self.fin_partida.hide()
                    #Guardamos toda la info posible en el controlador para después enviarsela al
                    # backend
                    self.id = mensaje["id"]
                    self.nombre_usuario = mensaje["nombre_usuario"]
                    self.host = mensaje["host"]
                    self.mostrar_ventana_sala_espera_signal.emit(mensaje)
            elif comando == "ingreso_rechazado":
                self.ventana_inicio.recibir_feedback_signal.emit(mensaje)
            elif comando == "actualizar_situaciones":
                self.ventana_sala_espera.actualizar_labels(mensaje)
            elif comando == "comenzar_partida":
                #Rellenamos el mensaje con información que teníamos guardada de antes
                mensaje["info_fotos"] = self.fotos
                mensaje["color_foto_usuario"] = self.color_foto
                mensaje["nombre_usuario"] = self.nombre_usuario
                mensaje["id"] = self.id
                self.backend_sala_juego.info_comienzo_partida(mensaje)
                self.mostrar_sala_juego_senal.emit(mensaje)
            elif comando == "nuevo_turno":
                self.backend_sala_juego.nuevo_turno(mensaje)
            elif comando == "termino_juego":
                self.senal_fin_partida.emit(mensaje)
            elif comando == "reingreso_rechazado":
                self.reingreso_rechazado(mensaje)
            elif comando == "setear_tiempo_turno":
                self.ventana_sala_juego.setear_tiempo(mensaje["segundos"])
        except TypeError:
            #El único mensaje que llega como lista es el de las fotos
            if self.es_primera_foto:
                self.color_foto = mensaje[1]
                self.fotos.append((mensaje[0], mensaje[1]))
                self.es_primera_foto = False
            else:
                self.fotos.append((mensaje[0], mensaje[1]))
        except KeyError:
            return []