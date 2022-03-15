from PyQt5 import uic
from PyQt5.QtCore import QPoint, pyqtSignal, Qt, QLine
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QApplication

from funcion_parametros import buscar_parametros as p
import sys

window_name_main, base_class_main = uic.loadUiType(p("ventana_sala_juego"))


class SalaJuego(window_name_main, base_class_main):

    senal_carta_baterias = pyqtSignal()
    recibir_feedback_signal = pyqtSignal(dict)
    senal_comprar_camino = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.fondo_azul.setPixmap(QPixmap(p("fondo_azul")))
        self.fondo_azul.setScaledContents(True)
        self.boton_sacar_carta.clicked.connect(self.sacar_carta)
        self.boton_comprar_camino.clicked.connect(self.comprar_camino)
        self.lineas = list()
        self.pmap_mapa = None

    def recibir_info_comienzo(self, mensaje):
        info_jugador = mensaje["info_jugador"]
        info_otros_jugadores = mensaje["info_otros_jugadores"]
        #Seteamos mapa
        if mensaje["mapa"] == "mapa_sanjoaquin":
            self.pmap_mapa = QPixmap(p("mapa_sanjoaquin"))
            self.imagen_mapa.setPixmap(self.pmap_mapa)
            self.imagen_mapa.setScaledContents(True)
            self.nombre_mapa.setText("Mapa San Joaquín")
        else:
            self.pmap_mapa = QPixmap(p("mapa_ingenieria"))
            self.imagen_mapa.setPixmap(self.pmap_mapa)
            self.imagen_mapa.setScaledContents(True)
            self.nombre_mapa.setText("Mapa Ingeniería")
        #Seteamos info jugador
        #Seteamos foto jugador, es lo único que no viene de info_jugador, y es porque se envió 
        #codificada al entrar
        pmap_foto_j = QPixmap()
        pmap_foto_j.loadFromData(info_jugador["bytes_foto"])
        self.foto_jugador.setPixmap(pmap_foto_j)
        self.foto_jugador.setScaledContents(True)
        #Seteamos el resto de la info del jugador
        self.nombre_jugador.setText(info_jugador["nombre"])
        self.turno_jugador.setText(str(info_jugador["turno"]))
        self.objetivo.setText(info_jugador["objetivo"][0] + " a " + info_jugador["objetivo"][1])
        #Seteamos info del resto de los jugadores, primero ordenaremos el diccionario para no tener 
        # fututos problemas
        info_otros_jugadores_orden = dict(sorted(info_otros_jugadores.items(), key=lambda x: \
                                                                                        int(x[0])))
        llaves_id = [llave for llave in info_otros_jugadores_orden.keys()]
        info_1 = info_otros_jugadores_orden[llaves_id[0]]
        self.turno_1.setText(str(info_1["turno"]))
        self.nombre_1.setText(info_1["nombre"])
        pmap_foto_1 = QPixmap()
        pmap_foto_1.loadFromData(info_1["bytes_foto"])
        self.foto_1.setPixmap(pmap_foto_1)        
        self.foto_1.setScaledContents(True)
        if p("cantidad_jugadores_partida") == 3 or p("cantidad_jugadores_partida") == 4:
            info_2 = info_otros_jugadores_orden[llaves_id[1]]
            self.turno_2.setText(str(info_2["turno"]))
            self.nombre_2.setText(info_2["nombre"])
            pmap_foto_2 = QPixmap()
            pmap_foto_2.loadFromData(info_2["bytes_foto"])
            self.foto_2.setPixmap(pmap_foto_2)
            self.foto_2.setScaledContents(True)
        if p("cantidad_jugadores_partida") == 4:
            info_3 = info_otros_jugadores_orden[llaves_id[2]]
            self.turno_3.setText(str(info_3["turno"]))
            self.nombre_3.setText(info_3["nombre"])
            pmap_foto_3 = QPixmap()
            pmap_foto_3.loadFromData(info_3["bytes_fotos"])
            self.foto_3.setPixmap(pmap_foto_3)
            self.foto_3.setScaledContents(True)
        self.recibir_info_turno(mensaje)

    def recibir_info_turno(self, mensaje):
        self.aviso.setText("")
        self.aviso.setStyleSheet("")
        info_jugador = mensaje["info_jugador"]
        info_otros_jugadores = mensaje["info_otros_jugadores"]
        self.baterias_jugador.setText(str(info_jugador["baterias"]))
        self.puntaje_jugador.setText(str(info_jugador["puntaje"]))
        info_otros_jugadores_orden = dict(sorted(info_otros_jugadores.items(), key=lambda x: \
                                                                                        int(x[0])))
        llaves_id = [llave for llave in info_otros_jugadores_orden.keys()]
        info_1 = info_otros_jugadores_orden[llaves_id[0]]
        self.baterias_1.setText(str(info_1["baterias"]))
        if p("cantidad_jugadores_partida") == 3 or p("cantidad_jugadores_partida") == 4:
            info_2 = info_otros_jugadores_orden[llaves_id[1]]
            self.baterias_2.setText(str(info_2["baterias"]))
        if p("cantidad_jugadores_partida") == 4:
            info_3 = info_otros_jugadores_orden[llaves_id[2]]
            self.baterias_3.setText(str(info_3["baterias"]))
        if info_jugador["objetivo_cumplido"]:
            self.objetivo.setStyleSheet("background-color: rgb(0, 170, 0);")
        #Seteamos turno actual
        self.turno_actual.setText(str(mensaje["turno_actual"]))
        self.jugador_actual.setText(mensaje["jugador_actual"])
        if mensaje["jugador_actual"] != info_jugador["nombre"]:
            self.boton_sacar_carta.setDisabled(True)
            self.boton_comprar_camino.setDisabled(True)
        elif mensaje["jugador_actual"] == info_jugador["nombre"]:
            self.boton_sacar_carta.setEnabled(True)
            self.boton_comprar_camino.setEnabled(True)
        try:
            lineas = mensaje["lineas"]
            self.dibujar_lineas(lineas)
        except KeyError:
            self.vaciar_mapa()
            pass

    def vaciar_mapa(self):
        #Significa que no hay líneas, y si está partiendo una nueva jugada
        #Queremos limpiar el mapa de jugadas anteriores
        self.imagen_mapa.clear()
        if self.nombre_mapa.text() == "Mapa Ingeniería":
            self.pmap_mapa = QPixmap(p("mapa_ingenieria"))
            self.imagen_mapa.setPixmap(self.pmap_mapa)
            self.imagen_mapa.setScaledContents(True)
            self.nombre_mapa.setText("Mapa Ingeniería")
        else:
            self.pmap_mapa = QPixmap(p("mapa_sanjoaquin"))
            self.imagen_mapa.setPixmap(self.pmap_mapa)
            self.imagen_mapa.setScaledContents(True)
            self.nombre_mapa.setText("Mapa San Joaquín")
    
    def setear_tiempo(self, segundos):
        self.tiempo.display(segundos)

    def esconder_ventana(self):
        self.hide()
        self.objetivo.setStyleSheet("background-color: rgb(255, 0, 0);")
        self.lineas = []

    def dibujar_lineas(self, lineas):
        #Actualizamos mapa
        for linea in lineas:
            if linea[0] == 1:
                color = Qt.blue
            elif linea[0] == 2:
                color = Qt.red
            elif linea[0] == 3:
                color = Qt.green
            else:
                color = Qt.yellow
            x_1, y_1 = linea[1]
            x_2, y_2 = linea[2]
            linea = [QLine(QPoint(x_1, y_1), QPoint(x_2, y_2)), color]
            if linea not in self.lineas:
                self.lineas.append(linea)
        self.update()

    def paintEvent(self, event):
        if len(self.lineas) != 0:
            painter = QPainter(self.pmap_mapa)
            for linea in self.lineas:
                pen = QPen(linea[1], 10)
                painter.setPen(pen)
                painter.drawLine(linea[0])    
            self.imagen_mapa.setPixmap(self.pmap_mapa)
            self.imagen_mapa.setScaledContents(True)

    def sacar_carta(self):
        self.senal_carta_baterias.emit()
        pass
    
    def comprar_camino(self):
        facultad_1 = self.facultad_comprada_1.text()
        facultad_2 = self.facultad_comprada_2.text()
        try:
            tupla_camino = (facultad_1.upper(), facultad_2.upper())
            self.senal_comprar_camino.emit(tupla_camino)
        except TypeError:
            self.aviso.setText("Debes ingresar valores válidos para el camino que desees comprar")
            self.aviso.setStyleSheet("background-color: rgb(255, 0, 0);")

    def mostrar_aviso(self, aviso):
        self.aviso.setStyleSheet("background-color: rgb(255, 0, 0);")
        self.aviso.setText(aviso)


if __name__ == "__main__":
    app = QApplication([])
    app.exec()
    ventana = SalaJuego()
    ventana.show()
    sys.exit()