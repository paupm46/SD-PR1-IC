from concurrent import futures
import time
from meteo_utils import MeteoDataProcessor
import redis
import pika
from datetime import datetime


class MeteoData:
    def __init__(self, temperature, humidity):
        self.temperature = temperature
        self.humidity = humidity


class PollutionData:
    def __init__(self, co2):
        self.co2 = co2


processor = MeteoDataProcessor()
r = redis.Redis(host='localhost', port=6379, db=0)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)


def callback(ch, method, properties, body):
    raw_data = str(body.decode()).split(":")
    sensor_type = raw_data[0]

    # En función del tipo de dato llamar a una función de procesamiento o otra
    if sensor_type == "a":
        wellness_data = processor.process_meteo_data(MeteoData(float(raw_data[1]), float(raw_data[2]))) # Procesar meteo data del air sensor
        r.set("m-" + str(raw_data[3]), str(wellness_data)) # Guardar valor obtenido con la clave m-timestamp en Redis
    else:
        p_data = processor.process_pollution_data(PollutionData(float(raw_data[1]))) # Procesar pollution data del pollution sensor
        r.set("p-" + str(raw_data[2]), str(p_data)) # Guardar valor obtenido con la clave p-timestamp en Redis

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)

channel.start_consuming()

