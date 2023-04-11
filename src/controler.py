#!/usr/bin/env python
import pika
import json
import argparse

class Controler:

    def __init__(self) -> None:
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='2391_1_controler_queue', durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='2391_1_controler_queue', on_message_callback=self.callback)
        self.orders = []
        self.registered_clients = []

    def content_dict(self):
        return {'orders': self.orders, 'registered_clients': self.registered_clients}

    def content_load(self, content):
        self.orders = content['orders']
        self.registered_clients = content['registered_clients']

    # Envia todos los pedidos al cliente
    def send_orders_to_client(self, body):
        client_id = body['client_id']
        client_orders = [order for order in self.orders if order['client_id'] == str(client_id)]
        body['orders'] = client_orders
        self.channel.basic_publish(exchange='', routing_key='2391_1_client_' + client_id + '_queue', body=json.dumps(body),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))

    # Envia el pedido al robot
    def send_order_to_robot(self,message):
        self.channel.basic_publish(exchange='', routing_key='2391_1_robot_task_queue', body=json.dumps(message),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))

    # Envia un mensaje al cliente cuando se ha registrado
    def send_registered_to_client(self, body):
        client_id = body['client_id']
        body['type'] = 'registered'
        message = json.dumps(body)
        self.channel.basic_publish(exchange='', routing_key='2391_1_client_' + client_id + '_queue', body=message,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          )) 
        
    # Envia un mensaje al cliente en caso de que no se haya registrado
    def send_not_registered_to_client(self, body):
        client_id = body['client_id']
        body['type'] = 'not_registered'
        self.channel.basic_publish(exchange='', routing_key='2391_1_client_' + client_id + '_queue', body=json.dumps(body),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))   

    # Envia a la cola de delivery en caso de que se haya encontrado el producto
    def send_order_to_delivery(self, body):
        self.channel.basic_publish(exchange='', routing_key='2391_1_delivery_queue', body=json.dumps(body),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))
    
    # Envia un mensaje al cliente en caso de que no se haya encontrado el producto
    def send_products_not_found_to_client(self, body):
        client_id = body['client_id']
        not_found_products = body['no_product']
        message = f'Products {not_found_products} not found.'
        self.channel.basic_publish(exchange='', routing_key='2391_1_client_' + client_id + '_queue', body=message,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))
        
    # Actualiza el estado de un pedido
    def update_order_status(self, order_id, status):
        for order in self.orders:
            if order['order_id'] == order_id:
                order['order_status'] = status

    # Envia un mensaje al cliente en caso de que se haya cancelado el pedido
    def send_order_canceled_to_client(self, body):
        client_id = body['client_id']
        body['type'] = 'canceled'
        message = json.dumps(body)
        self.channel.basic_publish(exchange='', routing_key='2391_1_client_' + client_id + '_queue', body=message,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))

    # Envia un mensaje al cliente en caso de que no se haya podido cancelar el pedido
    def send_cannot_cancel_order_to_client(self, body):
        client_id = body['client_id']
        body['type'] = 'cannot_cancel'
        self.channel.basic_publish(exchange='', routing_key='2391_1_client_' + client_id + '_queue', body=json.dumps(body),
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))

    def send_cannot_deliver_order_to_client(self, body):
        client_id = body['client_id']
        message = 'Cannot deliver order: ' + body['order_id'] + '.'
        self.channel.basic_publish(exchange='', routing_key='2391_1_client_' + client_id + '_queue', body=message,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))

    # Comprueba el estado de un pedido
    def check_order_status(self, order_id):
        for order in self.orders:
            if order['order_id'] == order_id:
                return order['order_status']

    def callback(self, ch, method, properties, body):
        print(" [x] Received %r" % body)
        message = json.loads(body)
        message_type = message.get('type')
        client_id = message.get('client_id')
        order_id = message.get('order_id')

        if message_type == 'register': # Registro
            self.registered_clients.append(client_id)
            print(f' [x] Client registered{client_id}')
            self.send_registered_to_client(message)
        elif message_type == 'purchase_order': # Comprar
            message['tries'] = 0
            if message.get('client_id') not in self.registered_clients:
                self.send_not_registered_to_client(message)
                print(f' [x] Client  not registered:{client_id}')
            else:
                self.update_order_status(order_id, 'processing')
                message['order_status'] = 'processing'
                self.orders.append(message)
                print(f' [x] Processing order:{order_id}')
                self.send_order_to_robot(message)

        elif message_type == 'see_orders': # Ver pedidos
            if message.get('client_id') not in self.registered_clients:
                self.send_not_registered_to_client(message)
                print(f' [x] Client  not registered:{client_id}')
            else:
                print(f' [x] Sending orders to client:{client_id}')
                self.send_orders_to_client(message)

        elif message_type == 'products_found' or message_type == 'retry': # Productos encontrados o reintentar
            if self.check_order_status(order_id) != 'canceled':
                self.update_order_status(order_id, 'in_delivery')
                message['order_status'] = 'in_delivery'
                print(f' [x] Sending order found to delivery:{order_id}')
                self.send_order_to_delivery(message)

        elif message_type == 'products_not_found': # Productos no encontrados
            if self.check_order_status(order_id) != 'canceled':
                self.update_order_status(order_id, 'not_found')
                message['order_status'] = 'not_found'
                print(f' [x] Sending order not found to client:{order_id}')
                self.send_products_not_found_to_client(message)

        elif message_type == 'cancel_order': # Cancelar pedido
            if message.get('client_id') not in self.registered_clients:
                self.send_not_registered_to_client(message)
                print(f' [x] Client  not registered:{client_id}')
            else:
                if self.check_order_status(order_id) == 'processing':
                    self.update_order_status(order_id, 'canceled')
                    message['order_status'] = 'canceled'
                    self.send_order_canceled_to_client(message)
                    print(f' [x] Sending order canceled to client:{order_id}')
                else:
                    self.send_cannot_cancel_order_to_client(message)
        elif message_type == 'cannot_deliver':
            self.update_order_status(order_id, 'cannot_deliver')
            message['order_status'] = 'cannot_deliver'
            print(f' [x] Sending order cannot deliver to client:{order_id}')
            self.send_cannot_deliver_order_to_client(message)
        elif message_type == 'delivered':
            self.update_order_status(order_id, 'finished')
            message['order_status'] = 'finished'
            print(f' [x] Order finished: {order_id}')
        ch.basic_ack(delivery_tag=method.delivery_tag)