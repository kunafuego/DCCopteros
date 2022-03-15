import pickle


CHUNK_SIZE_MENSAJE = 60
CHUNK_SIZE_IMAGEN = 100
"""
Modulo para funciones de codificacion y decodificacion para envio de mensajes.
Recuerda, no debes modificar los argumentos que recibe cada funcion,
y debes entregar exactamente lo que esta pide en el enunciado.
"""


def codificar_mensaje(mensaje):
    """
Esta función recibe un diccionario, el cual deberás
codificar según lo especificado en Envío de información. Ante lo cual, la función deberá retornar
un bytearray que cumpla la estructura correspondiente para un mensaje que no es una imagen de 
perfil
    """    
    mensaje_codificado = pickle.dumps(mensaje)
    bytes_largo_mensaje = len(mensaje_codificado).to_bytes(4, byteorder="big")
    bytes_tipo_mensaje = (2).to_bytes(4, byteorder="little")

    bytes_contenido = b""
    numero_bloque = 0
    for i in range(0, len(mensaje_codificado), CHUNK_SIZE_MENSAJE):
        bytes_numero_bloque = numero_bloque.to_bytes(4, byteorder="little")
        try:
            chunk = mensaje_codificado[i: i + CHUNK_SIZE_MENSAJE]
        except IndexError:
            pass
        while len(chunk) < CHUNK_SIZE_MENSAJE:
            chunk += b'\x00'
        bytes_contenido += (bytes_numero_bloque + chunk)
        numero_bloque += 1
    
    return bytearray(bytes_largo_mensaje + bytes_tipo_mensaje + bytes_contenido)


# Decodificar un bytearray para obtener el mensaje original.
def decodificar_mensaje(mensaje):
    
    bytes_mensaje = b""
    chunks_mensaje = []
    for i in range(8, len(mensaje) + 1, CHUNK_SIZE_MENSAJE + 4):
        chunk = mensaje[i + 4: i + CHUNK_SIZE_MENSAJE + 4]
        chunks_mensaje.append(chunk)
        """        if b"\x00" in chunk:
            indice = chunk.index(b"\x00")
            bytes_mensaje += chunk[:indice]
        else:
            bytes_mensaje += chunk
    """
    bytes_mensaje = b"".join(chunks_mensaje).strip(b"\x00")
    mensaje_json = pickle.loads(bytes_mensaje)
    return mensaje_json


# Codificar una imagen a un bytearray segun el protocolo especificado.
def codificar_imagen(ruta):
    # COMPLETAR ESTA FUNCION
    with open(ruta, "rb") as archivo_imagen:
        imagen_codificada = bytearray(archivo_imagen.read())

    bytes_largo_imagen = len(imagen_codificada).to_bytes(4, byteorder="big")
    bytes_tipo_imagen = (1).to_bytes(4, byteorder="little")
    bytes_color_imagen = int(ruta[18]).to_bytes(4, byteorder="big")
    bytes_contenido = b""
    numero_bloque = 0

    for i in range(0, len(imagen_codificada), CHUNK_SIZE_IMAGEN):
        bytes_numero_bloque = numero_bloque.to_bytes(4, byteorder="little")
        try:
            chunk = imagen_codificada[i: i + CHUNK_SIZE_IMAGEN]
        except IndexError:
            pass
        while len(chunk) < CHUNK_SIZE_IMAGEN:
            chunk += b'\x00'
        bytes_contenido += (bytes_numero_bloque + chunk)
        numero_bloque += 1
    
    return bytearray(bytes_largo_imagen + bytes_tipo_imagen + bytes_color_imagen + bytes_contenido)


# Decodificar un bytearray a una lista segun el protocolo especificado.
def decodificar_imagen(mensaje):
    int_color = int.from_bytes(mensaje[8:12], byteorder="big")
    chunks_imagenes = []
    for i in range(12, len(mensaje) + 1, CHUNK_SIZE_IMAGEN + 4):
        chunk = bytearray(mensaje[i + 4: i + CHUNK_SIZE_IMAGEN + 4])
        chunks_imagenes.append(chunk)

    bytes_imagen = bytearray(b"".join(chunks_imagenes).strip(b"\x00"))
    return [bytes_imagen, int_color]
    # COMPLETAR ESTA FUNCION
