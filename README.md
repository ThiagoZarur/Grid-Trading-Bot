# Grid-Trading-Bot
This is a grid trading bot develop with python



### Español:

Para iniciar podemos utilizar una maquina virtual en google cloud, o cualquier cloud o hacerlo de manera local 

De forma local, primero crear nuestro entorno virtual con python e instalar las librerías que utilizaremos

py -m venv "nombre del venv" #grid_trading

para instalar todos los paquetes 
pip install -r requirements.txt 

### Guardar tus keys en un entorno virtual

crear un archivo .env

poner en constantes tus llaves 

API_KEY = ''
PRIVATE_KEY = ''

y ahora los llamamos desde decouple 
Ejemplo:

from decouple import config

api_key =  config('API_KEY',default='')
secret = config('PRIVATE_KEY',default='')