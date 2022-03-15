from servidor import Servidor

if __name__ == "__main__":
    SERVIDOR = Servidor()

    try:
        while True:
            input("Presione Ctrl+C para cerrar el servidor...\n")
    except KeyboardInterrupt:
        print("\nCerrando servidor...")
        SERVIDOR.cerrar_servidor()
