from meteo_utils import MeteoDataDetector
import time
import pika
import sys

detector = MeteoDataDetector()

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

try:
    while True:
        time.sleep(1.0)
        pollution_data = detector.analyze_pollution() # Generar dato de polución
        timestamp = time.time_ns() # Crear timestamp actual
        message = str("p:" + str(pollution_data['co2']) + ":" + str(timestamp))
        channel.basic_publish(
            exchange='',
            routing_key='task_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))
except KeyboardInterrupt:
    connection.close()

