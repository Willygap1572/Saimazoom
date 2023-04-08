import pika
import sys
import random as rdm
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

binding_keys = sys.argv[1:]
if not binding_keys:
    sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
    sys.exit(1)

for binding_key in binding_keys:
    channel.queue_bind(
        exchange='topic_logs', queue=queue_name, routing_key=binding_key)

print(' [*] Waiting for logs. To exit press CTRL+C')
def callback(ch, method, properties, body):
    print(f"{method.routing_key}, {body}")
    no_product = []
    try:
        products = json.loads(body)['products']
        for item in products:
            if(rdm.random() > 0.95):
                no_product.append(item)
        if len(no_product) != 0:    
            channel.basic_publish(exchange='topic_logs', routing_key='saimazoom.NO_PRODUCT', body=no_product.__str__())

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()