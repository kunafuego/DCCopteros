import sys
from PyQt5.QtWidgets import QApplication
from cliente import Cliente


if __name__ == "__main__":
    # Se establece el host y port.
    # Puedes modificar estos valores si lo deseas.
    APP = QApplication(sys.argv)
    # Se instancia el Cliente.
    CLIENTE = Cliente()

    # Se inicia la app de PyQt.
    ret = APP.exec_()
    CLIENTE.socket_cliente.close()
    sys.exit()
