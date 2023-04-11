#!/usr/bin/env python
import pika
import time
import json
import random as rdm

class Delivery:
    def __init__(self, p_entrega):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='2391_1_delivery_queue', durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='2391_1_delivery_queue', on_message_callback=self.callback)
        self.p_entrega = p_entrega

    def send_product_delivered_to_controler(self, body):
        message = json.loads(body)
        message['type'] = 'delivered'
        message = json.dumps(message)
        self.channel.basic_publish(exchange='', routing_key='2391_1_controler_queue', body=message,
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # make message persistent
                              ))

    def send_cannot_deliver_to_controler(self, body):
        message = json.loads(body)
        message['tries'] = message['tries'] + 1
        if message['tries'] > 3:
            message['type'] = 'cannot_deliver'
        else:
            message['type'] = 'retry'
        message = json.dumps(message)
        self.channel.basic_publish(exchange='', routing_key='2391_1_controler_queue', body=message,
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # make message persistent
                              ))

    def callback(self, ch, method, properties, body):
        
        print(" [x] Received %r" % body)
        time.sleep(rdm.randint(10,20))
        if rdm.random() < self.p_entrega:
            self.send_product_delivered_to_controler(body)
        else:
            self.send_cannot_deliver_to_controler(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
