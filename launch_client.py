#!/usr/bin/env python
import pika
import json
import uuid

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

client_id = uuid.uuid4()
channel.queue_declare(queue='client_' + str(client_id) + '_queue', durable=True)

#message = ' '.join(sys.argv[1:]) or "Hello World!"
order_id = uuid.uuid4()
message = json.dumps({'order_id': str(order_id), 'products':['Raton', 'Teclado', 'Pantalla'], 'client_id': str(client_id)})
channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
    ))
print(" [x] Sent %r" % message)


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    channel.stop_consuming()

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='client_' + str(client_id) + '_queue', on_message_callback=callback)

channel.start_consuming()


