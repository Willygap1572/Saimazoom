#!/usr/bin/env python
import pika
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')
#channel.queue_declare(queue='robot_task_queue', durable=True)

def send_to_robot(body):
    channel.basic_publish(exchange='', routing_key='robot_task_queue', body=body,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body.decode())
    send_to_robot(body)
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)

channel.start_consuming()