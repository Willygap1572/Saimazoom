#!/usr/bin/env python
import pika
import time
import json
import random as rdm

class Robot:

    def __init__(self, p_almacen) -> None:
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='2391_1_robot_task_queue', durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='2391_1_robot_task_queue', on_message_callback=self.callback)
        self.p_almacen = p_almacen

    def enviar_productos_controlador(self, body):
        body = json.loads(body)
        body['type'] = 'products_found'
        self.channel.basic_publish(
            exchange='',
            routing_key='2391_1_controler_queue',
            body=json.dumps(body),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))
        print(" [x] Sent %r" % body)

    def enviar_no_product_controlador(self, no_product, body):
        message = json.loads(body)
        message['type'] = 'products_not_found'
        message['no_product'] = no_product
        message = json.dumps(message)
        self.channel.basic_publish(
            exchange='',
            routing_key='2391_1_controler_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))
        print(" [x] Sent %r" % message)

    def find_product(self, body):
        time.sleep(rdm.randint(5,10))
        no_product = []
        
        products = json.loads(body)['products']
        for item in products:
            if(rdm.random() > self.p_almacen):
                no_product.append(item)
        if len(no_product) != 0:    
            self.enviar_no_product_controlador(no_product, body)
        else:
            self.enviar_productos_controlador(body) 

    def callback(self, ch, method, properties, body):
        print(" [x] Received %r" % str(body))
        self.find_product(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)