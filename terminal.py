import time
from datetime import datetime
from concurrent import futures
import matplotlib.pyplot as plt
import pika
import threading


wellness_means = []
pollution_means = []
timestamps = []


def rabbitmq_thread():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='logs', queue=queue_name)

    print(' [*] Waiting for logs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(" [x] %r" % body.decode())
        coefficients = str(body.decode()).split(":")
        print(coefficients)
        global wellness_means
        wellness_means.append(float(coefficients[0]))
        global pollution_means
        pollution_means.append(float(coefficients[1]))
        global timestamps
        dt = datetime.fromtimestamp(int(coefficients[2]) / 1e9).strftime('%H:%M:%S.%f')
        timestamps.append(dt)
        animate(timestamps, wellness_means, pollution_means)

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()


rabbitmq_t = threading.Thread(target=rabbitmq_thread)
rabbitmq_t.start()

fig = plt.figure(figsize=(12, 6))
ax = plt.subplot(121)
ax2 = plt.subplot(122)


def animate(timestamps, wellness_means, pollution_means):
    timestamps = timestamps[-20:]
    wellness_means = wellness_means[-20:]
    pollution_means = pollution_means[-20:]

    ax.clear()
    ax.plot(timestamps, wellness_means)
    ax.tick_params(labelrotation=45)

    ax2.clear()
    ax2.plot(timestamps, pollution_means)
    ax2.tick_params(labelrotation=45)

    ax.title.set_text('Air wellness')
    ax2.title.set_text('Air pollution')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Coefficient')
    ax2.set_xlabel('Timestamp')
    ax2.set_ylabel('Coefficient')

    plt.subplots_adjust(bottom=0.30)
    plt.draw()


plt.show()


