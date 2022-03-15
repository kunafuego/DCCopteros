from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap

from funcion_parametros import buscar_parametros as p

window_name_main, base_class_main = uic.loadUiType(p("ventana_inicio"))


class VentanaInicio(window_name_main, base_class_main):

    senal_ingreso = pyqtSignal(dict)
    recibir_feedback_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label_logo.setPixmap(QPixmap(p("logo_transparente")))
        self.label_logo.setScaledContents(True)
        self.label_fondo.setPixmap(QPixmap(p("fondo_inicio")))
        self.label_fondo.setScaledContents(True)
        self.boton_comenzar.clicked.connect(self.verificar_usuario)
        #self.boton_salir.clicked.connect(self.salir_juego)
        #self.boton_rankings.clicked.connect(self.rankings)
        self.__conectar_eventos()
        
    def mostrar_ventana_inicio(self):
        self.show()

    def verificar_usuario(self):
        diccionario_indicacion = {
            "comando": "ingreso",
            "nombre_usuario": self.nombre.text()
        }
        self.senal_ingreso.emit(diccionario_indicacion)
    
    def esconder_ventana_inicio(self):
        self.hide()

    def __conectar_eventos(self):
        #Este método podrá conectar las señales de esta ventana con métodos de la misma.
        #Suena raro, pero es porque vamos a llamar las señales desde otro lado
        self.recibir_feedback_signal.connect(self.recibir_feedback)
    
    def recibir_feedback(self, mensaje):
        comentario = mensaje["comentario"]
        self.label_mensaje.setText(comentario)
        
