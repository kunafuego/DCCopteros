from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import QApplication

from funcion_parametros import buscar_parametros as p
import sys

window_name_main, base_class_main = uic.loadUiType(p("fin_partida"))


class FinPartida(window_name_main, base_class_main):

    senal_volver_a_jugar = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.fondo_azul.setPixmap(QPixmap(p("fondo_azul")))
        self.fondo_azul.setScaledContents(True)
        self.movie = QMovie(p("gif"))
        self.gif.setMovie(self.movie)
        self.gif.setScaledContents(True)
        self.volver_a_jugar.clicked.connect(self.funcion_volver_a_jugar)

    def mostrar_ventana(self, mensaje):
        # actualiza los labels
        usuarios = mensaje["usuarios"]
        usuarios_ordenados = dict(sorted(usuarios.items(), key=lambda item: item[1] 
                                                            ["puntaje_final"], reverse=True))
        id_en_orden = [id for id in usuarios_ordenados.keys()]
        cantidad_usuarios = len(usuarios)
        usuario_1 = usuarios_ordenados[id_en_orden[0]]
        self.nombre_1.setText(usuario_1["nombre"])
        self.puntaje_1.setText(str(usuario_1["puntaje_final"]) + "pts")
        usuario_2 = usuarios_ordenados[id_en_orden[1]]
        self.nombre_2.setText(usuario_2["nombre"])
        self.puntaje_2.setText(str(usuario_2["puntaje_final"]) + "pts")      
        if cantidad_usuarios == 3 or cantidad_usuarios == 4:
            usuario_3 = usuarios_ordenados[id_en_orden[2]]
            self.nombre_3.setText(usuario_3["nombre"])
            self.puntaje_3.setText(str(usuario_3["puntaje_final"]) + "pts")
        else:
            self.label_4.setVisible(False)
            self.label_6.setVisible(False)
        if cantidad_usuarios == 3:
            self.label_6.setVisible(False)
        if cantidad_usuarios == 4:
            usuario_4 = usuarios_ordenados[id_en_orden[3]]
            self.nombre_4.setText(usuario_4["nombre"])
            self.puntaje_4.setText(str(usuario_4["puntaje_final"]) + "pts")        
        self.movie.start()   
        self.show()

    def funcion_volver_a_jugar(self):
        self.senal_volver_a_jugar.emit()


if __name__ == "__main__":
    # Se establece el host y port.
    # Puedes modificar estos valores si lo deseas.
    APP = QApplication(sys.argv)
    # Se instancia el Cliente.
    fin_partida = FinPartida()
    fin_partida.mostrar_ventana({"as": 1})

    # Se inicia la app de PyQt.
    ret = APP.exec_()
    sys.exit()