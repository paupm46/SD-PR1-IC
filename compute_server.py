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
print(' [*] Waiting for messages. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body.decode())
    raw_data = str(body.decode()).split(":")
    print(raw_data)
    sensor_type = raw_data[0]

    if sensor_type == "a":
        wellness_data = processor.process_meteo_data(MeteoData(float(raw_data[1]), float(raw_data[2])))
        print(wellness_data)
        r.set("m-" + str(raw_data[3]), str(wellness_data))
        print(datetime.fromtimestamp(int(raw_data[3]) / 1e9).strftime('%H:%M:%S.%f'))
    else:
        p_data = processor.process_pollution_data(PollutionData(float(raw_data[1])))
        print(p_data)
        r.set("p-" + str(raw_data[2]), str(p_data))

    #time.sleep(body.count(b'.'))
    #print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)

channel.start_consuming()

