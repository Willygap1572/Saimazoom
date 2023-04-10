#!/usr/bin/env python
import pika
import time
import json
import random as rdm

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='delivery_task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

def send_product_to_client(body):
    client_id = json.loads(body)['client_id']
    channel.basic_publish(exchange='', routing_key='client_'+ client_id +'_queue', body=body,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    send_product_to_client(body)
    #esperar a que el repartidor llegue
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='delivery_task_queue', on_message_callback=callback)

channel.start_consuming()