# Tarea 3: Nombre de la tarea :school_satchel:


## Consideraciones generales :octocat:
¡Holaa! ¡Quedó muy buena la tarea! Pude implementar todo lo abarcado en el enunciado(o eso creo, se me puede haber pasado un detalle).
El modelamiento lo hice muy parecido al de la AF7. Por parte del cliente tengo:
La clase Cliente que maneja el socket, la clase Controlador que maneja los mensajes, hace de backend para las ventanas poco complejas y hace de mediador entre frontend
y backend en la ventana de juego, y además tengo un Backend para la ventana de juego(que hereda clases que ocupa de otro módulo) y una clase para cada
tipo de ventana, almacenadas en la carpeta ventanas dentro de la carpeta cliente.
Por parte del servidor tengo:
Una clase Servidor que maneja los sockets, una clase Logica que maneja los mensajes que recibe y da una respuesta a cada uno.

De todas maneras quisiera hacer varias aclaraciones sobre algunos temas:

Fotos:
En el enunciado decía que debíamos enviarle una foto al cliente al momento de conectarse con el servidor, 
pero luego en los logs del servidor decía que al enviar la foto debíamos escribir el nombre del cliente. Esto es un poco confuso, porque al momento de conectarse con el servidor el cliente aun no nos da su nombre de usuario.
Es por esto que se podrá ver en la consola del servidor el nombre del jugador y su avatar correspondiente a la hora de iniciar la partida, y no cuando esta es asignada al cliente.
Luego me dí cuenta que los Avatares solo pueden estar en la carpeta del servidor, por lo que mi algoritmo funcionó así:
Al conectarse el servidor a un cliente, el servidor le enviará una foto al azar, y el cliente lo que hará será guardar el color de esta.
Al comenzar la partida, el servidor le enviará al cliente **todas** las fotos, las cuales este almacenará y las enviará al backend del juego.
Luego para mostrarlas, el cliente ocupará la lista de usuarios, en la cual se especifica cual es el color de la foto de cada uno. 
De esta forma, al comenzar la partida el cliente le asigna a cada jugador los bytes de la foto que le corresponde, y así el cliente después lo muestra en el FE.
Ya sé que lo de mandar la foto al principio no tiene ningún sentido, pero lo hice para seguir lo que decía el enunciado.

Parametros:
Estaba muy entretenida la idea de tener los parametros en formato json. Para poder ocuparlos, cree un módulo llamado funcion_parametros.py, en el cual escribí 
dos funciones: una que se preocupa de las rutas y que deja los parametros en un formato de python, y otra que sirve para buscar un parametro específico. 
Los otros módulos deberán importar solamente la función para buscar los parametros.

Mapa:
**El mapa necesito que esté tanto en las carpetas de servidor como de cliente**, porque en la del servidor lo ocupé para designar los objetivos, y en la de cliente
para generar el grafo.



### Cosas implementadas y no implementadas :white_check_mark: :x:

La tarea ejecuta todo lo abarcado en el enunciado (o eso creo). Los dos bonus también fueron implementados.

## Ejecución :computer:
El módulo principal de la tarea a ejecutar es  ```main.py```. Además se debe crear los siguientes archivos y directorios adicionales:
Dentro de cliente/sprites debe estar la carpeta de Bonus, Logo y Mapas además de fondo_azul y fondo_inicio que son fotos agregadas por mí.
Dentro de cliente debe estar también mapa.json y parametros.json.
Dentro de servidor debe estar Avatares, mapa.json y parametros.json


## Librerías :books:
### Librerías externas utilizadas
La lista de librerías externas que utilicé fue la siguiente:

1. ```json```
2. ```random```: ```choice```, ```randint```, ```choices```
3. ```pickle```
4. ```PyQt5``` (se debe instalar)
5. ```threading```: ```Lock```, ```Thread```
6. ```collections```: ```deque```
7. ```time```: ```sleep```

### Librerías propias
Por otro lado, los módulos que fueron creados fueron los siguientes:

1. ```servidor.py```: Contiene a ```Servidor``` que maneja los sockets del servidor
2. ```logica.py```: Contiene a ```Logica``` que maneja los mensajes y respuestas del servidor
3. ```cliente.py```: Contiene a ```Cliente``` que maneja los sockets del cliente
4. ```interfaz.py```: Contiene a ```Controlador``` que maneja los mensajes y respuestas del cliente, y conecta los FE y BE de la ventana de juego
5. ```BE_sala_juego.py```: Contiene a ```BESalaJuego``` que contiene al backend del juego.
6. ```clasesBE.py```: Contiene a todas las clases que necesita BESalaJuego para funcionar (Threads, Grafo, etc..)
Además en ambas carpetas tengo los main.py(donde se ejecuta), funcion_parametros.py(funciones para manejar los parametros) y codificacion.py(módulo que maneja las codificaciones).

## Supuestos y consideraciones adicionales :thinking:
Había una conexión con costo 7 y no se especificaba en el enunciado a cuántos puntos correspondía esa cantidad de baterías. Asumí este valor como 20 puntos.
¡Te dejé comentado algo por si quieres hacer más fácil la corrección de la tarea! Es en logica.py en las líneas 214 a 217. Si las descomentas, el juego terminará al comprar el camino entre A y B.

Me quedan 9 minutos, pero tratré de escribir acá dónde está todo lo en amarillo de la distribución de puntaje:
El Networking está todo en los módulos cliente.py y servidor.py
Los locks, la separación y las responsabilidades se pueden ver en logica.py, interfaz.py y BE_sala_juego.py
La correcta separación entre FE y BE es evidente
El Grafo se ve todo en clasesBE.py. Me quedó bueno lo de poder enviar el Grafo como string, pero luego apenas le llega al cliente lo vuelve a pasar a Grafo(función generar_lista_adyacencia).
Lo de los archivos .json también es evidente.

¡Muchas gracias por todo!


## Referencias de código externo :book:

Ocupé código de la ayudantía 11 en la función decodificar imagenes, copié la idea de meter los chunks a una lista y luego stripearlos para que se vayan solo los ceros de al final.

Ocupé código de los contenidos para crear la estructura del grafo, la lista de adyacencia la cree por mi cuenta.

Ocupé código de https://www.geeksforgeeks.org/longest-path-undirected-tree/ para encontrar la ruta más larga que tenía cada id. De todas formas tuve que hacer una larga adaptación

Para realizar mi tarea saqué código de:
1. \<link de código>: este hace \<lo que hace> y está implementado en el archivo <nombre.py> en las líneas <número de líneas> y hace <explicación breve de que hace>



## Descuentos
La guía de descuentos se encuentra [link](https://github.com/IIC2233/syllabus/blob/master/Tareas/Descuentos.md).
