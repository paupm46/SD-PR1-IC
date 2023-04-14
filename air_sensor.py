from meteo_utils import MeteoDataDetector
import time
import pika
import sys
from datetime import datetime

detector = MeteoDataDetector()



connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

try:
    while True:
        time.sleep(1.0)
        meteo_data = detector.analyze_air()

        timestamp = time.time_ns()
        print(datetime.fromtimestamp(timestamp / 1e9).strftime('%H:%M:%S.%f'))

        message = str("a:" + str(meteo_data['temperature']) + ":" + str(meteo_data['humidity']) + ":" + str(timestamp))
        channel.basic_publish(
            exchange='',
            routing_key='task_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))

        print(" [x] Sent %r" % message)

        # print(meteo_data)
except KeyboardInterrupt:
    connection.close()

