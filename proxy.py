import time
import redis
from datetime import datetime
import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='fanout')

r = redis.Redis(host='localhost', port=6379, db=0)
t_interval = 5
t_marge = 4
time.sleep(5) # Esperar 5 segundos para que se calculen algunos datos
time_act = time.time_ns()
while True:
    time.sleep(t_interval)
    time_act = time_act + t_interval * 1000000000    # Mejor calcular el tiempo actual sumando 5s en el tiempo anterior pq time.sleep(5.0) no son exactamente 5 segundos y se podría quedar algún valor fuera
    min_timestamp = time_act - (t_interval+t_marge) * 1000000000
    max_timestamp = time_act - t_marge * 1000000000 # Dejo 4 segundos de margen por los valores que el sensor quita poco antes de empezar a calcular la media de los últimos 5s en el proxy, para que el compute_server tiene un tiempo de cálculo

    pattern = "m-*" # Obtener las claves de los valores de meteo
    n_values = 0
    wellness_mean = 0
    for key in r.scan_iter(match=pattern):
        # Extraer timestamp de la clave
        key_timestamp = int(str(key).split("-")[1].replace("'", ""))
        # Comprovar si el timestamp esta dentro del rango a calcular la mediana
        if key_timestamp >= min_timestamp and key_timestamp < max_timestamp:
            # Obtener valor almacenado en la clave
            wellness_data = r.get(key)
            wellness_data = float(str(wellness_data).split("'")[1].replace("'", ""))
            n_values = n_values + 1
            wellness_mean = wellness_mean + wellness_data
            r.delete(key)

    if n_values > 0:
        wellness_mean = wellness_mean/n_values # Calcular mediana de wellness (meteo)

    pattern = "p-*"
    n_values = 0
    pollution_mean = 0
    for key in r.scan_iter(match=pattern):
        # Extraer timestamp de la clave
        key_timestamp = int(str(key).split("-")[1].replace("'", ""))
        # Comprovar si el timestamp esta dentro del rango a calcular la mediana
        if key_timestamp >= min_timestamp and key_timestamp < max_timestamp:
            # Obtener valor almacenado en la clave
            pollution_data = r.get(key)
            pollution_data = float(str(pollution_data).split("'")[1].replace("'", ""))
            n_values = n_values + 1
            pollution_mean = pollution_mean + pollution_data
            r.delete(key)

    if n_values > 0:
        pollution_mean = pollution_mean/n_values # Calcular mediana de pollution

    message = str(str(wellness_mean)+":"+str(pollution_mean)+":"+str(max_timestamp))
    channel.basic_publish(exchange='logs', routing_key='', body=message)


connection.close()
