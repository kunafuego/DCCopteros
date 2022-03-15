from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap

from funcion_parametros import buscar_parametros as p
import sys

from PyQt5.QtWidgets import QApplication, QPushButton

window_name_main, base_class_main = uic.loadUiType(p("sala_de_espera"))


class SalaEspera(window_name_main, base_class_main):

    #senal_ingreso = pyqtSignal(dict)
    #recibir_feedback_signal = pyqtSignal(dict)
    senal_votar = pyqtSignal(dict)
    senal_comenzar_juego = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.fondo_azul.setPixmap(QPixmap(p("fondo_azul")))
        self.fondo.setPixmap(QPixmap(p("fondo_inicio")))
        self.mapa_1.setPixmap(QPixmap(p("mapa_ingenieria")))
        self.mapa_2.setPixmap(QPixmap(p("mapa_sanjoaquin")))
        self.fondo.setScaledContents(True)
        self.fondo_azul.setScaledContents(True)
        self.mapa_1.setScaledContents(True)
        self.mapa_2.setScaledContents(True)
        self.boton_votar.clicked.connect(self.votar)
        self.boton_iniciar.clicked.connect(self.comenzar_juego)


    def mostrar_sala_espera(self, mensaje):
        if mensaje["host"]:
            if self.boton_iniciar is not None:
                self.boton_iniciar.setDisabled(True)
            else:
                self.boton_iniciar = QPushButton("Iniciar", self)
                self.boton_iniciar.setGeometry(250, 50, 141, 31)
                self.boton_iniciar.clicked.connect(self.comenzar_juego)
                self.boton_iniciar.setDisabled(True)
        else:
            if self.boton_iniciar is not None:
                self.boton_iniciar.deleteLater()
                self.boton_iniciar = None
        self.show() 

    def actualizar_labels(self, mensaje):
        lista_usuarios = [usuario[0] for usuario in mensaje["usuarios"].values()]
        try:
            self.jugador_1.setText(lista_usuarios[0])
            self.jugador_2.setText(lista_usuarios[1])
            self.jugador_3.setText(lista_usuarios[2])
            self.jugador_4.setText(lista_usuarios[3])
        except IndexError:
            pass
        lista_votantes = [usuario[1] for usuario in mensaje["usuarios"].values()]
        try:
            self.situacion_1.setText(lista_votantes[0])
            self.situacion_2.setText(lista_votantes[1])
            self.situacion_3.setText(lista_votantes[2])
            self.situacion_4.setText(lista_votantes[3])
        except IndexError:
            pass
        lista_votos = [usuario[2] for usuario in mensaje["usuarios"].values()]
        votos_ingenieria = 0
        votos_sanjoaquin = 0
        for voto in lista_votos:
            if voto == "mapa_ingenieria":
                votos_ingenieria += 1
            elif voto == "mapa_sanjoaquin":
                votos_sanjoaquin += 1
        self.votos_ingenieria.display(votos_ingenieria)
        self.votos_sanjoaquin.display(votos_sanjoaquin)
        if None not in lista_votos and len(lista_usuarios) == p("cantidad_jugadores_partida") \
                                                                and self.boton_iniciar is not None:
            #Si no están todos los cupos ocupados, todos ya votaronm y 
            #el jugador es host activamos el botón de iniciar
            self.boton_iniciar.setEnabled(True)

    def comenzar_juego(self):
        diccionario_indicacion = dict()
        diccionario_indicacion["comando"] = "comenzar_juego"
        self.senal_comenzar_juego.emit(diccionario_indicacion)

    def esconder_sala_espera(self):
        self.jugador_1.setText("")
        self.jugador_2.setText("")
        self.jugador_3.setText("")
        self.jugador_4.setText("")
        self.situacion_1.setText("")
        self.situacion_2.setText("")
        self.situacion_3.setText("")
        self.situacion_4.setText("")
        self.hide()

    def votar(self):
        diccionario_indicacion_voto = dict()
        diccionario_indicacion_voto["comando"] = "votar"
        if (self.check_mapa_1.isChecked() and self.check_mapa_2.isChecked()) or \
            (not self.check_mapa_1.isChecked() and not self.check_mapa_2.isChecked()):
            self.aviso.setText("Debes marcar una opción")
        elif self.check_mapa_1.isChecked():
            diccionario_indicacion_voto["opcion_elegida"] = "mapa_ingenieria"
            self.senal_votar.emit(diccionario_indicacion_voto)
        elif self.check_mapa_2.isChecked():
            diccionario_indicacion_voto["opcion_elegida"] = "mapa_sanjoaquin"
            self.senal_votar.emit(diccionario_indicacion_voto)


if __name__ == "__main__":
    app = QApplication([])
    salaespera = SalaEspera()
    salaespera.show()
    ret = app.exec_()
    sys.exit()

