import src.client as c
import sys
import os  

def main():
    print('Este programa simula a un cliente registrandose, haciendo pedidos y viendo sus pedidos')
    client = c.Client()
    client.client_register()
    client.order_products(['productX', 'productX'])
    client.order_products(['productY', 'productY'])
    client.see_orders()
    try:
        client.channel.start_consuming()
    except Exception as e:
        print(e)
        client.channel.stop_consuming()
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


