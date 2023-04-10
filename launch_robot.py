#!/usr/bin/env python
import pika
import time
import json
import random as rdm

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='robot_task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

def enviar_no_product_cliente(no_product, body):
    client_id = json.loads(body)['client_id']
    channel.basic_publish(exchange='', routing_key='client_'+ client_id +'_queue', body=json.dumps({'order_id': json.loads(body)['order_id'], 'no_products':no_product}),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))

def enviar_productos_repartidor(body):
    channel.basic_publish(exchange='', routing_key='delivery_task_queue', body=body,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))

def find_product(body):
    no_product = []
    try:
        products = json.loads(body)['products']
        for item in products:
            if(rdm.random() > 0.95):
                no_product.append(item)
        if len(no_product) != 0:    
            enviar_no_product_cliente(no_product, body)
        else:
            enviar_productos_repartidor(body) 

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    find_product(body)
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='robot_task_queue', on_message_callback=callback)

channel.start_consuming()