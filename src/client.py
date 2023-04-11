import pika
import json
import uuid
from datetime import date
import sys
import os

class Client:
    def __init__(self) -> None:
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        self.client_id = uuid.uuid4()
        self.channel.queue_declare(queue='2391_1_client_' + str(self.client_id) + '_queue', durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='2391_1_client_' + str(self.client_id) + '_queue', on_message_callback=self.callback)

    def __str__(self) -> str:
        return f"Client({self.client_id})"

    def client_register(self):
        message = {'client_id': str(self.client_id)}
        message['type'] = 'register'
        message = json.dumps(message)
        self.channel.basic_publish(
            exchange='',
            routing_key='2391_1_controler_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))
        

    def cancel_order(self, order_id):
        message = {'client_id': str(self.client_id), 'order_id': str(order_id)}
        message['type'] = 'cancel_order'
        message = json.dumps(message)
        self.channel.basic_publish(
            exchange='',
            routing_key='2391_1_controler_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))
        
        print(" [x] Sent %r" % message)

    def order_products(self, products):
        order_id = uuid.uuid4()
        message = {'client_id': str(self.client_id), 'order_id': str(order_id), 'products': products}
        message['type'] = 'purchase_order'
        message = json.dumps(message)
        self.channel.basic_publish(
            exchange='',
            routing_key='2391_1_controler_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))
        
        print(" [x] Sent %r" % message)
        
        return str(order_id)

    def send_finish_order(self, body):
        message = json.loads(body)
        message['type'] = 'order_finished'
        message = json.dumps(message)
        self.channel.basic_publish(
            exchange='',
            routing_key='2391_1_controler_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))
        print(" [x] Sent %r" % message)

    def see_orders(self):
        message = {'client_id': str(self.client_id)}
        message['type'] = 'see_orders'
        message = json.dumps(message)
        self.channel.basic_publish(
            exchange='',
            routing_key='2391_1_controler_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))
        print(" [x] Sent %r" % message)

    def callback(self, ch, method, properties, body):
        message_type = json.loads(body)['type']
        if message_type == 'products_delivered':
            print('Your order has been completed')
            ch.basic_ack(delivery_tag=method.delivery_tag)
            self.send_finish_order(body)
            
        elif message_type == 'registered':
            print('Your are registered')
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        elif message_type == 'not_registered':
            print('Your are not registered')
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        elif message_type == 'see_orders':
            print('Your orders are:' + str(json.loads(body)['orders']))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        elif message_type == 'canceled':
            print('Your order has been canceled: ' + str(json.loads(body)['order_id']))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        elif message_type == 'cannot_cancel':
            print('Your order has not been canceled: ' + str(json.loads(body)['order_id']))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        elif message_type == 'product_not_found':
            print('Your order products has not been found: ' + str(json.loads(body)['no_product']))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        
            
        