import json
import os


def crear_parametros():
    parametros = {}
    with open("parametros.json", encoding='utf-8') as archivo:
        for parametro in json.load(archivo).items():
            try:
                if "/" in parametro[1]:
                    direcciones = parametro[1].split("/")
                    parametros[parametro[0]] = os.path.join(*direcciones)
                else:
                    parametros[parametro[0]] = parametro[1]
            except TypeError:
                parametros[parametro[0]] = parametro[1]
                
    return parametros

def buscar_parametros(llave):
    parametros = crear_parametros()
    return parametros[llave]